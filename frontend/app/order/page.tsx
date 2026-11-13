"use client";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, UploadCloud, FileBox, ShieldCheck, Layers3, Ruler, Box, Info } from "lucide-react";
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader.js";
import { ThreeMFLoader } from "three/examples/jsm/loaders/3MFLoader.js";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
function csrfToken(){return document.cookie.split("; ").find(row=>row.startsWith("csrftoken="))?.split("=")[1]||"";}
type Material = { id:number; name:string; technology:"FDM"|"RESIN"; price_per_gram_toman:number };
type Option = { id:number; key:string; label:string; value:string; technology:string };
type Machine = {id:number;name:string;technology:string;build_x_mm:number;build_y_mm:number;build_z_mm:number};
type ModelInfo = {x:number;y:number;z:number;volume:number};

export default function OrderPage() {
  const [file,setFile] = useState<File|null>(null);
  const [technology,setTechnology] = useState<"FDM"|"RESIN">("FDM");
  const [materials,setMaterials] = useState<Material[]>([]);
  const [options,setOptions] = useState<Option[]>([]);
  const [machines,setMachines] = useState<Machine[]>([]);
  const [modelInfo,setModelInfo] = useState<ModelInfo|null>(null);
  const [fileError,setFileError] = useState("");
  const [material,setMaterial] = useState("");
  const [infill,setInfill] = useState("20");
  const [layer,setLayer] = useState("0.20");
  const [nozzle,setNozzle] = useState("0.40");
  const [supports,setSupports] = useState(true);
  const [quantity,setQuantity] = useState(1);
  const [message,setMessage] = useState("برای ثبت سفارش باید وارد حساب کاربری شوید.");
  const [busy,setBusy] = useState(false);

  useEffect(() => {
    fetch(`${API}/materials/`).then(r=>r.ok?r.json():[]).then((data:Material[])=>setMaterials(data)).catch(()=>setMaterials([]));
    fetch(`${API}/machines/`).then(r=>r.ok?r.json():[]).then((data:Machine[])=>setMachines(data)).catch(()=>setMachines([]));
  }, []);
  useEffect(() => {
    fetch(`${API}/options/?technology=${technology}`).then(r=>r.ok?r.json():[]).then((data:Option[])=>{
      setOptions(data);
      const first = (key:string, fallback:string) => data.find(o=>o.key===key)?.value || fallback;
      setInfill(first("infill","20")); setLayer(first("layer_height","0.20"));
      setNozzle(first("nozzle_diameter","0.40"));
      const support = data.filter(o=>o.key==="supports").map(o=>o.value);
      if (support.length) setSupports(support.includes("true"));
    }).catch(()=>setOptions([]));
    setMaterial("");
  }, [technology]);
  useEffect(() => {
    let cancelled = false;
    async function inspectModel() {
      setModelInfo(null); setFileError("");
      if (!file) return;
      if (file.size > 100*1024*1024) { setFileError("حجم فایل نباید بیشتر از ۱۰۰ مگابایت باشد."); return; }
      try {
        const ext = file.name.toLowerCase().split(".").pop();
        const buffer = await file.arrayBuffer();
        let root: THREE.Object3D;
        if (ext === "stl") {
          // STLLoader returns BufferGeometry, not an Object3D. Wrap it in a Mesh
          // so bounds, transforms and traversal work consistently with OBJ/3MF.
          const geometry = new STLLoader().parse(buffer);
          root = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial());
        } else if (ext === "obj") root = new OBJLoader().parse(await file.text());
        else if (ext === "3mf") root = new ThreeMFLoader().parse(buffer);
        else throw new Error("فرمت فایل پشتیبانی نمی‌شود.");
        root.updateMatrixWorld(true);
        const bounds = new THREE.Box3().setFromObject(root);
        if (bounds.isEmpty()) throw new Error("هندسه قابل تشخیص در فایل پیدا نشد.");
        const size = bounds.getSize(new THREE.Vector3());
        let signedVolume = 0;
        root.traverse(node => {
          if (!(node instanceof THREE.Mesh)) return;
          const geometry = node.geometry;
          const position = geometry.getAttribute("position");
          const index = geometry.getIndex();
          const count = index ? index.count : position.count;
          const a = new THREE.Vector3(), b = new THREE.Vector3(), d = new THREE.Vector3();
          for (let i=0;i+2<count;i+=3) {
            const ia=index?index.getX(i):i, ib=index?index.getX(i+1):i+1, ic=index?index.getX(i+2):i+2;
            a.fromBufferAttribute(position,ia).applyMatrix4(node.matrixWorld);
            b.fromBufferAttribute(position,ib).applyMatrix4(node.matrixWorld);
            d.fromBufferAttribute(position,ic).applyMatrix4(node.matrixWorld);
            signedVolume += a.dot(b.clone().cross(d))/6;
          }
        });
        if (!cancelled) setModelInfo({x:size.x,y:size.y,z:size.z,volume:Math.abs(signedVolume)/1000});
      } catch (error) {
        if (!cancelled) setFileError(error instanceof Error?error.message:"خواندن فایل ممکن نشد.");
      }
    }
    inspectModel();
    return () => {cancelled=true;};
  }, [file]);

  const availableMaterials = useMemo(()=>materials.filter(m=>m.technology===technology),[materials,technology]);
  const values = (key:string) => options.filter(o=>o.key===key).map(o=>o.value);
  const infillOptions = values("infill");
  const layerOptions = values("layer_height");
  const compatibleLayerOptions = layerOptions.filter(v=>Number(v)<=Number(nozzle)*0.75).sort((a,b)=>Number(a)-Number(b));
  const nozzleOptions = values("nozzle_diameter");
  const supportOptions = values("supports");
  const compatibleMachines = machines.filter(m=>m.technology===technology);
  const fitsMachine = modelInfo && compatibleMachines.some(m=>modelInfo.x<=m.build_x_mm && modelInfo.y<=m.build_y_mm && modelInfo.z<=m.build_z_mm);

  async function submit(e: React.FormEvent) {
    e.preventDefault();

    if (!file) { setMessage("لطفاً فایل سه‌بعدی را انتخاب کنید."); return; }
    if (fileError) { setMessage(fileError); return; }
    if (modelInfo && compatibleMachines.length>0 && !fitsMachine) { setMessage("ابعاد فایل با دستگاه‌های فعال این تکنولوژی سازگار نیست."); return; }
    if (!material) { setMessage("ابتدا یک متریال فعال از فهرست انتخاب کنید."); return; }
    setBusy(true);
    const data = new FormData();
    data.append("file",file); data.append("technology",technology); data.append("material",material);
    if (infillOptions.length>0) data.append("infill_percent",infill);
    if (layerOptions.length>0) data.append("layer_height_mm",layer);
    if (nozzleOptions.length>0) data.append("nozzle_diameter_mm",nozzle);
    if (supportOptions.length>0) data.append("supports",String(supports));
    data.append("quantity",String(quantity));
    if (modelInfo) { data.append("model_volume_cm3",String(modelInfo.volume)); data.append("model_height_mm",String(modelInfo.z)); }
    try {
      const res = await fetch(`${API}/orders/`, {method:"POST",body:data,credentials:"include",headers:{"X-CSRFToken":decodeURIComponent(csrfToken())}});
      const body = await res.json().catch(()=>({}));
      if (res.status === 401 || res.status === 403) setMessage("نشست ورود شما معتبر نیست یا منقضی شده است؛ دوباره وارد حساب شوید.");
      else if (!res.ok) setMessage(body.detail || "ثبت سفارش انجام نشد؛ اطلاعات و اتصال API را بررسی کنید.");
      else {
        const estimate = `وزن تخمینی: ${Number(body.estimated_weight_g||0).toFixed(2)} گرم | زمان تخمینی: ${Number(body.estimated_hours||0).toFixed(2)} ساعت | مبلغ اولیه: ${Number(body.estimated_price_toman||0).toLocaleString("fa-IR")} تومان`;
        setMessage(`سفارش ثبت شد. ${estimate} — این مبلغ برآورد اولیه است و پس از اسلایس واقعی و بررسی کارشناس نهایی می‌شود.${technology === "RESIN" ? " برآورد رزین بر اساس زمان نوردهی دستگاه است؛ مدل‌های توخالی ممکن است وزن واقعی کمتری داشته باشند." : ""}`);
      }
    } catch { setMessage("ارتباط با سرور برقرار نشد."); }
    finally { setBusy(false); }
  }

  return <main className="order-page">
    <div className="order-wrap">
      <a href="/" className="back-link"><ArrowRight size={16}/> بازگشت به صفحه اصلی</a>
      <div className="order-heading"><span className="section-kicker">شروع یک پروژه جدید</span><h1>ثبت سفارش چاپ سه‌بعدی</h1><p>فایل مدل را بارگذاری و مشخصات اولیه را انتخاب کنید. برآورد نهایی پس از بررسی فنی اعلام می‌شود.</p></div>
      <form onSubmit={submit} className="order-form">
        <div className="form-section"><div className="form-title"><span><UploadCloud/></span><div><b>۱. فایل مدل سه‌بعدی</b><small>فرمت‌های STL، OBJ و 3MF · حداکثر ۱۰۰ مگابایت</small></div></div>
          <label className="upload-zone"><input required type="file" accept=".stl,.obj,.3mf" onChange={e=>setFile(e.target.files?.[0]||null)}/><FileBox size={30}/><b>{file?file.name:"فایل سه‌بعدی را انتخاب کنید"}</b><small>{file?`${(file.size/1024/1024).toFixed(2)} مگابایت`:"یا فایل را اینجا انتخاب کنید"}</small></label>
        </div>
        {fileError&&<div className="form-message">{fileError}</div>}
        {modelInfo&&<div className="model-inspection"><div className="model-inspection-title"><Ruler size={19}/><b>تحلیل هندسی فایل</b><span>محاسبه در مرورگر</span></div><div className="model-measures"><div><small>طول X</small><b>{modelInfo.x.toFixed(1)} mm</b></div><div><small>عرض Y</small><b>{modelInfo.y.toFixed(1)} mm</b></div><div><small>ارتفاع Z</small><b>{modelInfo.z.toFixed(1)} mm</b></div><div><small>حجم هندسی</small><b>{modelInfo.volume.toFixed(2)} cm³</b></div></div><div className={compatibleMachines.length===0?"model-fit unknown":fitsMachine?"model-fit good":"model-fit bad"}><Box size={16}/>{compatibleMachines.length===0?"ابعاد دستگاه‌ها هنوز توسط مدیر ثبت نشده است.":fitsMachine?"ابعاد مدل با حداقل یکی از دستگاه‌های فعال سازگار است.":"ابعاد مدل از محدوده تمام دستگاه‌های فعال این تکنولوژی بزرگ‌تر است."}</div><p><Info size={14}/> ابعاد بر اساس واحد میلی‌متر فرض شده‌اند. این تحلیل هندسی جایگزین Slicer نیست؛ وزن، زمان و قیمت نهایی پس از برش واقعی مدل مشخص می‌شود.</p></div>}
        <div className="form-section"><div className="form-title"><span><Layers3/></span><div><b>۲. مشخصات چاپ</b><small>فقط گزینه‌های فعال و متناسب با تکنولوژی نمایش داده می‌شوند</small></div></div>
          <label className="field-label">تکنولوژی چاپ</label>
          <div className="technology-choice"><button type="button" className={technology==="FDM"?"tech active":"tech"} onClick={()=>setTechnology("FDM")}><b>FDM</b><small>فیلامنتی</small></button><button type="button" className={technology==="RESIN"?"tech active":"tech"} onClick={()=>setTechnology("RESIN")}><b>RESIN</b><small>رزینی</small></button></div>
          <div className="form-grid">
            <label className="field-label">متریال<select required value={material} onChange={e=>setMaterial(e.target.value)}><option value="">انتخاب متریال</option>{availableMaterials.map(m=><option key={m.id} value={m.id}>{m.name}</option>)}</select></label>
            {infillOptions.length>0&&<label className="field-label">تراکم داخلی<select value={infill} onChange={e=>setInfill(e.target.value)}>{infillOptions.map((v,i)=><option key={`${v}-${i}`} value={v}>{v}٪</option>)}</select></label>}
            {layerOptions.length>0&&<label className="field-label">ارتفاع لایه (میلی‌متر)<select value={layer} onChange={e=>setLayer(e.target.value)}>{compatibleLayerOptions.map((v,i)=><option key={`${v}-${i}`} value={v}>{v}</option>)}</select></label>}
            {nozzleOptions.length>0&&<label className="field-label">قطر نازل (میلی‌متر)<select value={nozzle} onChange={e=>{const value=e.target.value;setNozzle(value);const valid=layerOptions.filter(v=>Number(v)<=Number(value)*0.75).sort((a,b)=>Number(a)-Number(b));if(valid.length&&Number(layer)>Number(value)*0.75)setLayer(valid[valid.length-1]);}}>{nozzleOptions.map((v,i)=><option key={`${v}-${i}`} value={v}>{v}</option>)}</select></label>}
            <label className="field-label">تعداد قطعه<input type="number" min="1" max="100" value={quantity} onChange={e=>setQuantity(Math.max(1,Math.min(100,+e.target.value||1)))}/></label>
          </div>
          {supportOptions.length>0&&<label className="field-label">ساپورت<select value={String(supports)} onChange={e=>setSupports(e.target.value==="true")}><option value="true" disabled={!supportOptions.includes("true")}>با ساپورت</option><option value="false" disabled={!supportOptions.includes("false")}>بدون ساپورت</option></select></label>}
        </div>
        <div className="estimate-note"><ShieldCheck/><span><b>برآورد اولیه وزن، زمان و قیمت</b><small>برای FDM، وزن و زمان با حجم هندسی، چگالی متریال، تراکم، نازل، لایه و تعرفه دستگاه تخمین زده می‌شود. این عدد جایگزین خروجی PrusaSlicer نیست و قیمت نهایی پس از بررسی فایل اعلام می‌شود. برای رزین، زمان از ارتفاع مدل، ضخامت لایه و زمان نوردهی و بالاآمدن هر لایه تخمین زده می‌شود؛ مدل‌های توخالی ممکن است وزن واقعی کمتری داشته باشند.</small></span></div>
        <button className="btn submit-order" disabled={busy}>{busy?"در حال ارسال...":"ارسال سفارش برای بررسی"} <ArrowRight size={18}/></button>
        <div role="status" className="form-message">{message} <a href="/login">ورود / ثبت‌نام</a></div>
      </form>
    </div>
  </main>;
}
