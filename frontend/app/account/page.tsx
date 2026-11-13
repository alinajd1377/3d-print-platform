"use client";

import { useEffect, useState, FormEvent } from "react";
import { ArrowRight, Save, LogOut, ClipboardList } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
type Profile = {mobile:string;full_name:string;address:string;postal_code:string};
type Order = {public_id:string;technology:string;material_name:string;status:string;final_price_toman:number|null;created_at:string};
type StoreOrder = {id:number;status:string;total_toman:number;created_at:string;coordination_note:string;items:{product:string;color:string;quantity:number}[]};
const statusNames:Record<string,string>={DRAFT:"پیش‌نویس",REVIEW:"در انتظار بررسی",QUOTED:"پیش‌فاکتور صادر شده",PAID:"پرداخت شده",PRINTING:"در حال چاپ",READY:"آماده تحویل",SHIPPED:"ارسال شده",COMPLETED:"تکمیل شده",REJECTED:"رد شده"};

export default function AccountPage() {
  const [profile,setProfile] = useState<Profile>({mobile:"",full_name:"",address:"",postal_code:""});
  const [orders,setOrders] = useState<Order[]>([]);
  const [storeOrders,setStoreOrders] = useState<StoreOrder[]>([]);
  const [message,setMessage] = useState("");
  const [busy,setBusy] = useState(false);
  const auth = () => typeof window!=="undefined" ? sessionStorage.getItem("authHeader") || "" : "";

  useEffect(()=>{
    const header=auth();
    if(!header){setMessage("برای مشاهده حساب کاربری ابتدا وارد شوید.");return;}
    const headers={Authorization:header};
    Promise.all([
      fetch(`${API}/profile/`,{headers}).then(r=>r.ok?r.json():null),
      fetch(`${API}/orders/`,{headers}).then(r=>r.ok?r.json():[]),
      fetch(`${API}/store/orders/`,{headers}).then(r=>r.ok?r.json():[])
    ]).then(([p,o,s])=>{if(p)setProfile(p);setOrders(Array.isArray(o)?o:(o.results||[]));setStoreOrders(Array.isArray(s)?s:[]);})
      .catch(()=>setMessage("دریافت اطلاعات با خطا مواجه شد."));
  },[]);

  async function save(e:FormEvent){
    e.preventDefault();setBusy(true);
    try{
      const response=await fetch(`${API}/profile/`,{method:"PATCH",headers:{"Content-Type":"application/json",Authorization:auth()},body:JSON.stringify({full_name:profile.full_name,address:profile.address,postal_code:profile.postal_code})});
      const data=await response.json().catch(()=>({}));
      setMessage(response.ok?"اطلاعات پروفایل ذخیره شد.":(data.detail||"ذخیره اطلاعات انجام نشد."));
    }catch{setMessage("ارتباط با سرور برقرار نشد.");}
    finally{setBusy(false);}
  }

  function logout(){sessionStorage.removeItem("authHeader");window.location.href="/login";}

  return <main className="account-page"><div className="account-wrap">
    <a className="back-link" href="/"><ArrowRight size={16}/> صفحه اصلی</a>
    <header className="account-heading"><div><span className="section-kicker">پنل مشتری</span><h1>حساب کاربری من</h1></div><button className="logout-btn" onClick={logout}><LogOut size={16}/> خروج</button></header>
    {!auth() ? <div className="store-message">{message} <a href="/login">ورود / ثبت‌نام</a></div> : <>
      <form className="account-panel" onSubmit={save}><h2>اطلاعات تماس و ارسال</h2>
        <label>شماره موبایل<input value={profile.mobile} readOnly/></label>
        <label>نام و نام خانوادگی<input value={profile.full_name} onChange={e=>setProfile({...profile,full_name:e.target.value})}/></label>
        <label>کد پستی<input value={profile.postal_code} onChange={e=>setProfile({...profile,postal_code:e.target.value})}/></label>
        <label>نشانی<textarea rows={3} value={profile.address} onChange={e=>setProfile({...profile,address:e.target.value})}/></label>
        <button className="btn" disabled={busy}>{busy?"در حال ذخیره":"ذخیره اطلاعات"} <Save size={16}/></button>
        {message&&<div className="form-message">{message}</div>}
      </form>
      <section className="account-panel"><h2><ClipboardList size={19}/> سفارش‌های چاپ من</h2>
        {orders.length===0?<p className="account-muted">هنوز سفارش چاپی ثبت نشده است.</p>:<div className="account-orders">{orders.map(o=><article key={o.public_id}><div><b>{o.material_name} · {o.technology}</b><small>{new Date(o.created_at).toLocaleDateString("fa-IR")}</small></div><span>{statusNames[o.status]||o.status}</span><strong>{o.final_price_toman?new Intl.NumberFormat("fa-IR").format(o.final_price_toman)+" تومان":"در انتظار قیمت نهایی"}</strong></article>)}</div>}
      </section>
    </>}
  </div></main>;
}
