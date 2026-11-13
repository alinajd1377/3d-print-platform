"use client";

import { useEffect, useState } from "react";
import { ArrowRight, ShoppingBag, PackageCheck } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
type Variant = { id:number; color:string; price_toman:number; stock:number };
type Product = { id:number; title:string; slug:string; description:string; variants:Variant[] };

const toman = (value:number) => new Intl.NumberFormat("fa-IR").format(value) + " تومان";

export default function StorePage() {
  const [products,setProducts] = useState<Product[]>([]);
  const [busy,setBusy] = useState<number|null>(null);
  const [message,setMessage] = useState("برای ثبت سفارش کالا، ابتدا باید وارد حساب کاربری شوید.");
  useEffect(() => {
    fetch(`${API}/store/products/`).then(r=>r.ok?r.json():[]).then(setProducts).catch(()=>setMessage("دریافت محصولات با خطا مواجه شد."));
  }, []);

  async function order(variantId:number) {
    setBusy(variantId);
    try {
      const response = await fetch(`${API}/store/orders/`, {
        method:"POST", credentials:"include",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({variant_id:variantId,quantity:1})
      });
      const result = await response.json().catch(()=>({}));
      if (response.status===401 || response.status===403) setMessage("برای ثبت سفارش ابتدا باید وارد حساب کاربری شوید.");
      else if (!response.ok) setMessage(result.detail || "ثبت سفارش انجام نشد.");
      else setMessage(result.message + " شماره سفارش: " + result.order_id);
    } catch { setMessage("ارتباط با سرور برقرار نشد."); }
    finally { setBusy(null); }
  }

  return <main className="store-page"><div className="store-wrap">
    <a className="back-link" href="/"><ArrowRight size={16}/> بازگشت به صفحه اصلی</a>
    <header className="store-heading"><span className="section-kicker">فروشگاه قطعات آماده</span><h1>محصولات آماده پرینت‌یار</h1><p>محصول را انتخاب کن و رنگ و موجودی هر گزینه را ببین.</p></header>
    {products.length===0 ? <div className="store-empty"><ShoppingBag size={32}/><b>هنوز محصولی برای نمایش ثبت نشده است.</b><span>مدیر سایت می‌تواند محصولات را از پنل مدیریت اضافه کند.</span></div> :
      <div className="store-grid">{products.map(product=><article className="store-card" key={product.id}>
        <div className="store-art"><PackageCheck size={42}/></div>
        <h2>{product.title}</h2><p>{product.description}</p>
        <div className="variant-list">{product.variants.map(v=><div className="variant-row" key={v.id}>
          <span>{v.color}<small>{v.stock>0?`موجودی: ${v.stock}`:"ناموجود / نیازمند هماهنگی"}</small></span>
          <b>{toman(v.price_toman)}</b>
          <button disabled={busy!==null || v.stock===0} onClick={()=>order(v.id)}>{busy===v.id?"...":"سفارش"}</button>
        </div>)}</div>
      </article>)}</div>}
    <div className="store-message" role="status">{message}</div>
  </div></main>;
}
