"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, LockKeyhole, UserRound } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode,setMode] = useState<"login"|"register">("login");
  const [mobile,setMobile] = useState("");
  const [password,setPassword] = useState("");
  const [fullName,setFullName] = useState("");
  const [message,setMessage] = useState("");
  const [busy,setBusy] = useState(false);

  async function submit(e:FormEvent) {
    e.preventDefault(); setBusy(true); setMessage("");
    try {
      const response = await fetch(`${API}/auth/mobile/`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({action:mode,mobile,password,full_name:fullName})
      });
      const data = await response.json().catch(()=>({}));
      if (!response.ok) { setMessage(data.detail || "ورود یا ثبت‌نام انجام نشد."); return; }
      sessionStorage.setItem("authHeader", "Basic " + btoa(mobile + ":" + password));
      router.push("/account");
    } catch { setMessage("ارتباط با سرور برقرار نشد."); }
    finally { setBusy(false); }
  }

  return <main className="auth-page"><div className="auth-card">
    <a className="back-link" href="/"><ArrowRight size={16}/> بازگشت به سایت</a>
    <div className="auth-icon"><UserRound size={25}/></div>
    <h1>{mode==="login"?"ورود به حساب کاربری":"ساخت حساب کاربری"}</h1>
    <p>با شماره موبایل و رمز عبور وارد سامانه شوید.</p>
    <div className="auth-tabs"><button className={mode==="login"?"selected":""} onClick={()=>setMode("login")}>ورود</button><button className={mode==="register"?"selected":""} onClick={()=>setMode("register")}>ثبت‌نام</button></div>
    <form onSubmit={submit} className="auth-form">
      {mode==="register"&&<label>نام و نام خانوادگی<input value={fullName} onChange={e=>setFullName(e.target.value)} required/></label>}
      <label>شماره موبایل<input inputMode="numeric" autoComplete="tel" value={mobile} onChange={e=>setMobile(e.target.value)} placeholder="09xxxxxxxxx" required/></label>
      <label>رمز عبور<input type="password" autoComplete={mode==="login"?"current-password":"new-password"} minLength={8} value={password} onChange={e=>setPassword(e.target.value)} required/></label>
      <small>رمز عبور حداقل ۸ کاراکتر است. ورود پیامکی در مرحله بعد با اتصال سرویس پیامک اضافه می‌شود.</small>
      <button className="btn" disabled={busy}>{busy?"لطفاً صبر کنید":mode==="login"?"ورود":"ایجاد حساب"} <LockKeyhole size={16}/></button>
      {message&&<div className="form-message" role="alert">{message}</div>}
    </form>
  </div></main>;
}
