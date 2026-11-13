"use client";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, UploadCloud, FileBox, ShieldCheck, Layers3 } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
type Material = { id:number; name:string; technology:"FDM"|"RESIN"; price_per_gram_toman:number };
type Option = { id:number; key:string; label:string; value:string; technology:string };

export default function OrderPage() {
  const [file,setFile] = useState<File|null>(null);
  const [technology,setTechnology] = useState<"FDM"|"RESIN">("FDM");
  const [materials,setMaterials] = useState<Material[]>([]);
  const [options,setOptions] = useState<Option[]>([]);
  const [material,setMaterial] = useState("");
  const [infill,setInfill] = useState("20");
  const [layer,setLayer] = useState("0.20");
  const [nozzle,setNozzle] = useState("0.40");
  const [color,setColor] = useState("");
  const [supports,setSupports] = useState(true);
  const [quantity,setQuantity] = useState(1);
  const [message,setMessage] = useState("برای ثبت سفارش باید وارد حساب کاربری شوید.");
  const [busy,setBusy] = useState(false);

  useEffect(() => {
    fetch(`${API}/materials/`).then(r=>r.ok?r.json():[]).then((data:Material[])=>setMaterials(data)).catch(()=>setMaterials([]));
  }, []);
  useEffect(() => {
    fetch(`${API}/options/?technology=${technology}`).then(r=>r.ok?r.json():[]).then((data:Option[])=>{
      setOptions(data);
      const first = (key:string, fallback:string) => data.find(o=>o.key===key)?.value || fallback;
      setInfill(first("infill","20")); setLayer(first("layer_height","0.20"));
      setNozzle(first("nozzle_diameter","0.40")); setColor(first("color",""));
      const support = data.filter(o=>o.key==="supports").map(o=>o.value);
      if (support.length) setSupports(support.includes("true"));
    }).catch(()=>setOptions([]));
    setMaterial(""); setColor("");
  }, [technology]);
  const availableMaterials = useMemo(()=>materials.filter(m=>m.technology===technology),[materials,technology]);
  const values = (key:string) => options.filter(o=>o.key===key).map(o=>o.value);
  const infillOptions = values("infill");
  const layerOptions = values("layer_height");
  const nozzleOptions = values("nozzle_diameter");
  const colorOptions = values("color");
  const supportOptions = values("supports");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const auth = sessionStorage.getItem("authHeader");
    if (!auth) { setMessage("برای ثبت سفارش ابتدا وارد حساب کاربری شوید."); return; }\n    if (!file) { setMessage("لطفاً فایل سه‌بعدی را انتخاب کنید."); return; }
    if (!material) { setMessage("ابتدا یک متریال فعال از فهرست انتخاب کنید."); return; }
    setBusy(true);
    const data = new FormData();
    data.append("file",file); data.append("technology",technology); data.append("material",material);
    if (infillOptions.length>0) data.append("infill_percent",infill);
    if (layerOptions.length>0) data.append("layer_height_mm",layer);
    if (nozzleOptions.length>0) data.append("nozzle_diameter_mm",nozzle);
    if (supportOptions.length>0) data.append("supports",String(supports));
    data.append("quantity",String(quantity));
    if (color) data.append("color",color);
    try {
      const res = await fetch(`${API}/orders/`, {method:"POST",body:data,credentials:"include",headers:{Authorization:auth}});
      const body = await res.json().catch(()=>({}));
      if (res.status === 401 || res.status === 403) setMessage("برای ثبت سفارش ابتدا باید وارد حساب کاربری شوید. ورود با شماره موبایل در مرحله بعد تکمیل می‌شود.");
      else if (!res.ok) setMessage(body.detail || "ثبت سفارش انجام نشد؛ اطلاعات و اتصال API را بررسی کنید.");
      else setMessage("سفارش ثبت شد و برای بررسی فنی ارسال می‌شود. وزن، زمان و مبلغ نهایی پس از بررسی اعلام خواهد شد.");
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
        <div className="form-section"><div className="form-title"><span><Layers3/></span><div><b>۲. مشخصات چاپ</b><small>فقط گزینه‌های فعال و متناسب با تکنولوژی نمایش داده می‌شوند</small></div></div>
          <label className="field-label">تکنولوژی چاپ</label>
          <div className="technology-choice"><button type="button" className={technology==="FDM"?"tech active":"tech"} onClick={()=>setTechnology("FDM")}><b>FDM</b><small>فیلامنتی</small></button><button type="button" className={technology==="RESIN"?"tech active":"tech"} onClick={()=>setTechnology("RESIN")}><b>RESIN</b><small>رزینی</small></button></div>
          <div className="form-grid">
            <label className="field-label">متریال<select required value={material} onChange={e=>setMaterial(e.target.value)}><option value="">انتخاب متریال</option>{availableMaterials.map(m=><option key={m.id} value={m.id}>{m.name}</option>)}</select></label>
            {colorOptions.length>0&&<label className="field-label">رنگ<select value={color} onChange={e=>setColor(e.target.value)}><option value="">انتخاب رنگ</option>{colorOptions.map((v,i)=><option key={`${v}-${i}`} value={v}>{v}</option>)}</select></label>}
            {infillOptions.length>0&&<label className="field-label">تراکم داخلی<select value={infill} onChange={e=>setInfill(e.target.value)}>{infillOptions.map((v,i)=><option key={`${v}-${i}`} value={v}>{v}٪</option>)}</select></label>}
            {layerOptions.length>0&&<label className="field-label">ارتفاع لایه (میلی‌متر)<select value={layer} onChange={e=>setLayer(e.target.value)}>{layerOptions.map((v,i)=><option key={`${v}-${i}`} value={v}>{v}</option>)}</select></label>}
            {nozzleOptions.length>0&&<label className="field-label">قطر نازل (میلی‌متر)<select value={nozzle} onChange={e=>setNozzle(e.target.value)}>{nozzleOptions.map((v,i)=><option key={`${v}-${i}`} value={v}>{v}</option>)}</select></label>}
            <label className="field-label">تعداد قطعه<input type="number" min="1" max="100" value={quantity} onChange={e=>setQuantity(Math.max(1,Math.min(100,+e.target.value||1)))}/></label>
          </div>
          {supportOptions.length>0&&<label className="field-label">ساپورت<select value={String(supports)} onChange={e=>setSupports(e.target.value==="true")}><option value="true" disabled={!supportOptions.includes("true")}>با ساپورت</option><option value="false" disabled={!supportOptions.includes("false")}>بدون ساپورت</option></select></label>}
        </div>
        <div className="estimate-note"><ShieldCheck/><span><b>برآورد دقیق پس از بررسی</b><small>ابعاد، وزن و زمان چاپ توسط فرایند فنی تعیین می‌شود؛ امکان ورود دستی این مقادیر برای مشتری غیرفعال است.</small></span></div>
        <button className="btn submit-order" disabled={busy}>{busy?"در حال ارسال...":"ارسال سفارش برای بررسی"} <ArrowRight size={18}/></button>
        <div role="status" className="form-message">{message} <a href="/login">ورود / ثبت‌نام</a></div>
      </form>
    </div>
  </main>;
}
