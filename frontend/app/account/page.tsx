"use client";

import { useEffect, useState, FormEvent } from "react";
import { ArrowRight, Save, LogOut, UserRound, MapPin, Printer, ShoppingBag, CreditCard } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
function csrfToken(){return document.cookie.split("; ").find(row=>row.startsWith("csrftoken="))?.split("=")[1]||"";}
type Profile = {mobile:string;full_name:string;address:string;postal_code:string};
type Order = {public_id:string;technology:string;material_name:string;original_filename:string;quantity:number;estimated_weight_g:string;estimated_hours:string;status:string;final_price_toman:number|null;payment_status:string;payment_amount_toman:number|null;payment_invoice_id:number|null;created_at:string};
type StoreOrder = {id:number;status:string;total_toman:number;created_at:string;coordination_note:string;items:{product:string;color:string;quantity:number}[]};
const statusNames:Record<string,string>={DRAFT:"پیش‌نویس",REVIEW:"در انتظار بررسی",QUOTED:"پیش‌فاکتور صادر شده",PAID:"پرداخت شده",PRINTING:"در حال چاپ",READY:"آماده تحویل",SHIPPED:"ارسال شده",COMPLETED:"تکمیل شده",REJECTED:"رد شده"};
const paymentNames:Record<string,string>={NOT_INVOICED:"هنوز فاکتور صادر نشده",PENDING:"منتظر پرداخت",PAID:"پرداخت تأیید شده",CANCELLED:"پرداخت لغو شده",FAILED:"پرداخت ناموفق",VERIFY_ERROR:"خطا در تأیید پرداخت"};

export default function AccountPage() {
  const [profile,setProfile] = useState<Profile>({mobile:"",full_name:"",address:"",postal_code:""});
  const [orders,setOrders] = useState<Order[]>([]);
  const [storeOrders,setStoreOrders] = useState<StoreOrder[]>([]);
  const [message,setMessage] = useState("");
  const [busy,setBusy] = useState(false);
  const [authenticated,setAuthenticated] = useState(false);
  const [section,setSection] = useState("profile");

  async function loadOrders(){
    const [o,s]=await Promise.all([
      fetch(`${API}/orders/`,{credentials:"include"}).then(r=>r.ok?r.json():[]),
      fetch(`${API}/store/orders/`,{credentials:"include"}).then(r=>r.ok?r.json():[])
    ]);
    setOrders(Array.isArray(o)?o:(o.results||[]));setStoreOrders(Array.isArray(s)?s:[]);
  }
  useEffect(()=>{
    fetch(`${API}/profile/`,{credentials:"include"})
      .then(async r=>{if(!r.ok){setAuthenticated(false);setMessage("برای مشاهده حساب کاربری ابتدا وارد شوید.");return null;}return r.json();})
      .then(p=>{if(!p)return;setAuthenticated(true);setProfile(p);return loadOrders();})
      .catch(()=>setMessage("دریافت اطلاعات با خطا مواجه شد."));
  },[]);

  async function save(e:FormEvent){
    e.preventDefault();setBusy(true);
    try{
      const response=await fetch(`${API}/profile/`,{method:"PATCH",credentials:"include",headers:{"Content-Type":"application/json","X-CSRFToken":decodeURIComponent(csrfToken())},body:JSON.stringify({full_name:profile.full_name,address:profile.address,postal_code:profile.postal_code})});
      const data=await response.json().catch(()=>({}));
      setMessage(response.ok?"اطلاعات پروفایل ذخیره شد.":(data.detail||"ذخیره اطلاعات انجام نشد."));
    }catch{setMessage("ارتباط با سرور برقرار نشد.");}
    finally{setBusy(false);}
  }
  async function pay(invoiceId:number){
    setBusy(true);setMessage("");
    try{
      const response=await fetch(`${API}/invoices/${invoiceId}/pay/`,{method:"POST",credentials:"include",headers:{"X-CSRFToken":decodeURIComponent(csrfToken())}});
      const data=await response.json().catch(()=>({}));
      if(response.ok&&data.payment_url)window.location.href=data.payment_url;
      else setMessage(data.detail||"درگاه پرداخت در دسترس نیست. وضعیت سفارش تا تأیید پرداخت تغییر نمی‌کند.");
    }catch{setMessage("ارتباط با درگاه پرداخت برقرار نشد.");}
    finally{setBusy(false);}
  }
  async function logout(){
    try{await fetch(`${API}/auth/mobile/`,{method:"POST",credentials:"include",headers:{"Content-Type":"application/json","X-CSRFToken":decodeURIComponent(csrfToken())},body:JSON.stringify({action:"logout"})});}
    finally{window.location.href="/login";}
  }

  const menu=[{id:"profile",label:"مشخصات کاربری",Icon:UserRound},{id:"address",label:"آدرس",Icon:MapPin},{id:"print",label:"سفارشات پرینت",Icon:Printer},{id:"store",label:"سفارشات خرید",Icon:ShoppingBag}];
  return <main className="account-page"><div className="account-wrap">
    <a className="back-link" href="/"><ArrowRight size={16}/> صفحه اصلی</a>
    <header className="account-heading"><div><span className="section-kicker">پنل مشتری</span><h1>حساب کاربری من</h1></div></header>
    {!authenticated ? <div className="store-message">{message} <a href="/login">ورود / ثبت‌نام</a></div> : <div className="account-layout">
      <aside className="account-sidebar">
        <div className="account-user"><b>{profile.full_name||"کاربر پرینت‌یار"}</b><small>{profile.mobile}</small></div>
        {menu.map(({id,label,Icon})=><button key={id} className={section===id?"account-menu active":"account-menu"} onClick={()=>{setSection(id);setMessage("");}}><Icon size={17}/>{label}</button>)}
        <button className="account-menu account-logout" onClick={logout}><LogOut size={17}/>خروج</button>
      </aside>
      <div className="account-content">
        {section==="profile"&&<form className="account-panel" onSubmit={save}><h2>مشخصات کاربری</h2>
          <label>شماره موبایل<input value={profile.mobile} readOnly/></label>
          <label>نام و نام خانوادگی<input value={profile.full_name} onChange={e=>setProfile({...profile,full_name:e.target.value})}/></label>
          <button className="btn" disabled={busy}>{busy?"در حال ذخیره":"ذخیره اطلاعات"} <Save size={16}/></button>
        </form>}
        {section==="address"&&<form className="account-panel" onSubmit={save}><h2>نشانی و اطلاعات ارسال</h2>
          <label>کد پستی<input value={profile.postal_code} onChange={e=>setProfile({...profile,postal_code:e.target.value})}/></label>
          <label>نشانی کامل<textarea rows={4} value={profile.address} onChange={e=>setProfile({...profile,address:e.target.value})}/></label>
          <button className="btn" disabled={busy}>{busy?"در حال ذخیره":"ذخیره آدرس"} <Save size={16}/></button>
        </form>}
        {section==="print"&&<section className="account-panel"><h2>سفارشات پرینت</h2>
          {orders.length===0?<p className="account-muted">هنوز سفارش چاپی ثبت نشده است.</p>:<div className="account-orders">{orders.map(o=><article key={o.public_id}><div><b>{o.material_name} · {o.technology}</b><small>{o.original_filename||"فایل مدل"} · تعداد: {o.quantity||1} · {new Date(o.created_at).toLocaleDateString("fa-IR")}</small><small>وزن تخمینی: {o.estimated_weight_g||"—"} گرم · زمان: {o.estimated_hours||"—"} ساعت</small></div><span>{statusNames[o.status]||o.status}</span><strong>{o.final_price_toman?new Intl.NumberFormat("fa-IR").format(o.final_price_toman)+" تومان":"در انتظار قیمت نهایی"}</strong><small className="payment-state"><CreditCard size={14}/>{paymentNames[o.payment_status]||o.payment_status}</small>{o.status==="QUOTED"&&o.payment_invoice_id&&o.payment_status!=="PAID"&&<button className="btn" type="button" disabled={busy} onClick={()=>pay(o.payment_invoice_id!)}>پرداخت فاکتور</button>}</article>)}</div>}
        </section>}
        {section==="store"&&<section className="account-panel"><h2>سفارشات خرید</h2>
          {storeOrders.length===0?<p className="account-muted">هنوز سفارش کالایی ثبت نشده است.</p>:<div className="account-orders">{storeOrders.map(o=><article key={o.id}><div><b>{o.items.map(i=>i.product+" · "+i.color+" × "+i.quantity).join("، ")}</b><small>{new Date(o.created_at).toLocaleDateString("fa-IR")}</small>{o.coordination_note&&<small>{o.coordination_note}</small>}</div><span>{o.status==="COORDINATION"?"نیازمند هماهنگی موجودی":o.status==="PENDING"?"در انتظار بررسی":o.status}</span><strong>{new Intl.NumberFormat("fa-IR").format(o.total_toman)} تومان</strong></article>)}</div>}
        </section>}
        {message&&<div className="form-message" role="status">{message}</div>}
      </div>
    </div>}
  </div></main>;
}
