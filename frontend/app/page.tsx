import { Printer, Layers3, ShieldCheck, Clock3, UploadCloud, Calculator, PackageCheck, Sparkles, ArrowLeft, Box, Cpu } from "lucide-react";

const services = [
  { icon: <Printer size={23}/>, title: "چاپ فیلامنتی FDM", text: "برای قطعات کاربردی، نمونه‌سازی مهندسی و تولید با متریال‌های متنوع." },
  { icon: <Layers3 size={23}/>, title: "چاپ رزینی دقیق", text: "جزئیات ظریف، سطوح صاف و مدل‌های کوچک با دقت بالا." },
  { icon: <Calculator size={23}/>, title: "برآورد شفاف هزینه", text: "برآورد اولیه آنلاین و اعلام پیش‌فاکتور نهایی پس از بررسی فنی." },
];

export default function Home() {
  return <>
    <header className="topbar"><div className="container nav">
      <a className="logo" href="/"><span className="logo-mark"><Box size={21}/></span> پرینت‌یار <small>3D PRINT</small></a>
      <nav className="navlinks"><a href="#services">خدمات</a><a href="/store">فروشگاه</a><a href="/account">حساب کاربری</a><a href="#steps">مراحل سفارش</a><a href="#why">چرا ما؟</a></nav>
      <a className="btn nav-cta" href="/order">ثبت سفارش <ArrowLeft size={17}/></a>
    </div></header>
    <main>
      <section className="hero"><div className="hero-orb orb-one"/><div className="hero-orb orb-two"/>
        <div className="container hero-grid">
          <div className="hero-copy">
            <div className="eyebrow"><Sparkles size={16}/> از ایده تا قطعه واقعی</div>
            <h1>مدل سه‌بعدی‌ات را<br/><span>واقعی چاپ کن.</span></h1>
            <p>فایل طراحی‌ات را بارگذاری کن، روش چاپ و متریال مناسب را انتخاب کن و سفارش را برای بررسی تخصصی بفرست. باقی مسیر با ماست.</p>
            <div className="hero-actions"><a className="btn" href="/order">شروع سفارش <ArrowLeft size={18}/></a><a className="btn ghost" href="#services">مشاهده خدمات</a></div>
            <div className="hero-points"><span><ShieldCheck size={16}/> بررسی فنی پیش از تولید</span><span><Cpu size={16}/> FDM و رزینی</span></div>
          </div>
          <div className="hero-visual">
            <div className="visual-glow"/>
            <div className="visual-card"><div className="visual-top"><span className="live-dot"/> استودیو چاپ سه‌بعدی</div>
              <div className="printer-art"><div className="printer-frame"><div className="printer-rail"/><div className="printer-head"/><div className="print-bed"/><div className="printed-object"/></div></div>
              <div className="visual-caption"><div><b>دقت در جزئیات</b><small>کیفیت، متریال و اجرای حرفه‌ای</small></div><span className="visual-icon"><Box size={22}/></span></div>
            </div>
            <div className="float-chip chip-a">FDM <span>●</span></div><div className="float-chip chip-b">RESIN <span>✦</span></div>
          </div>
        </div>
        <div className="container hero-bottom"><span>یک فایل سه‌بعدی کافی است</span><span className="bottom-line"/><span>ما آن را به محصول تبدیل می‌کنیم</span></div>
      </section>
      <section className="section" id="services"><div className="container">
        <div className="section-heading"><div><span className="section-kicker">خدمات ما</span><h2>برای هر مدل، یک راه‌حل دقیق</h2></div><p className="sub">با توجه به کاربرد قطعه، تکنولوژی و متریال مناسب را انتخاب می‌کنیم.</p></div>
        <div className="cards">{services.map((s,i)=><article className="card service-card" key={s.title}><div className="iconbox">{s.icon}</div><span className="card-index">۰{i+1}</span><h3>{s.title}</h3><p>{s.text}</p></article>)}</div>
      </div></section>
      <section className="section process-section" id="steps"><div className="container">
        <div className="section-heading"><div><span className="section-kicker">مسیر سفارش</span><h2>چهار قدم تا قطعه نهایی</h2></div><p className="sub">تمام مراحل سفارش را می‌توانی از پنل کاربری پیگیری کنی.</p></div>
        <div className="steps">
          <div className="step"><b>۰۱</b><h3>بارگذاری فایل</h3><p>مدل STL، OBJ یا 3MF خودت را ارسال کن.</p></div>
          <div className="step"><b>۰۲</b><h3>انتخاب روش چاپ</h3><p>تکنولوژی، متریال و گزینه‌های قابل‌دسترس را انتخاب کن.</p></div>
          <div className="step"><b>۰۳</b><h3>بررسی و پیش‌فاکتور</h3><p>کارشناس فایل را بررسی و مبلغ نهایی را اعلام می‌کند.</p></div>
          <div className="step"><b>۰۴</b><h3>تولید و تحویل</h3><p>پس از تأیید و پرداخت، سفارش وارد مرحله تولید می‌شود.</p></div>
        </div>
      </div></section>
      <section className="section why-section" id="why"><div className="container why-grid">
        <div><span className="section-kicker">تجربه‌ای مطمئن</span><h2>از فایل تا ساخت،<br/>همراهت هستیم.</h2><p className="sub">پیش از صدور فاکتور نهایی، امکان‌پذیری چاپ و تنظیمات فنی بررسی می‌شود تا هزینه و نتیجه قابل‌پیش‌بینی‌تر باشد.</p><a className="text-link" href="/order">سفارش خود را ثبت کن <ArrowLeft size={17}/></a></div>
        <div className="why-list"><div><ShieldCheck/><span><b>کنترل کیفیت فنی</b><small>بررسی فایل و سازگاری تنظیمات پیش از تولید</small></span></div><div><Clock3/><span><b>شفافیت در وضعیت سفارش</b><small>پیگیری مراحل از پنل کاربری</small></span></div><div><PackageCheck/><span><b>اطلاع‌رسانی تا تحویل</b><small>نمایش وضعیت آماده‌سازی و ارسال</small></span></div></div>
      </div></section>
    </main>
    <footer className="footer"><div className="container footer-inner"><a className="logo" href="/">پرینت‌یار <small>3D PRINT</small></a><span>© پرینت‌یار — سامانه سفارش آنلاین چاپ سه‌بعدی</span></div></footer>
  </>;
}
