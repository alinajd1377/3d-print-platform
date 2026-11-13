"use client";

import { useEffect, useState } from "react";
import { Phone, Mail, MapPin, Clock3, Instagram, Send, MessageCircle, AtSign, ExternalLink } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
type Settings = {site_name:string;contact_phone:string;contact_email:string;telegram_url:string;bale_url:string;instagram_url:string;x_url:string;whatsapp_url:string;contact_address:string;working_hours:string};

export default function SiteChrome() {
  const [settings,setSettings] = useState<Settings|null>(null);
  useEffect(()=>{fetch(`${API}/site-settings/`).then(r=>r.ok?r.json():null).then(setSettings).catch(()=>setSettings(null));},[]);
  const links = settings ? [
    {label:"تلفن",href:settings.contact_phone?`tel:${settings.contact_phone.replace(/[^+0-9]/g,"")}`:"",Icon:Phone},
    {label:"واتساپ",href:settings.whatsapp_url,Icon:MessageCircle},
    {label:"تلگرام",href:settings.telegram_url,Icon:Send},
    {label:"بله",href:settings.bale_url,Icon:MessageCircle},
    {label:"اینستاگرام",href:settings.instagram_url,Icon:Instagram},
    {label:"ایکس / توییتر",href:settings.x_url,Icon:AtSign},
  ].filter(x=>x.href) : [];
  return <footer className="global-footer">
    <div className="global-footer-inner">
      <div className="global-footer-brand"><a href="/" className="logo">پرینت‌یار <small>3D PRINT</small></a><p>از فایل سه‌بعدی تا قطعه واقعی، همراه شما هستیم.</p></div>
      <div className="global-footer-contact"><b>راه‌های ارتباطی</b><div className="global-socials">{links.map(({label,href,Icon})=><a key={label} href={href} aria-label={label} title={label} target={href.startsWith("http")?"_blank":undefined} rel="noreferrer"><Icon size={18}/><span>{label}</span></a>)}</div>
        {settings?.contact_email&&<a className="footer-detail" href={`mailto:${settings.contact_email}`}><Mail size={15}/>{settings.contact_email}</a>}
        {settings?.contact_address&&<span className="footer-detail"><MapPin size={15}/>{settings.contact_address}</span>}
        {settings?.working_hours&&<span className="footer-detail"><Clock3 size={15}/>{settings.working_hours}</span>}
      </div>
    </div>
    <div className="global-footer-bottom">© {new Date().getFullYear()} {settings?.site_name||"پرینت‌یار"} — تمامی حقوق محفوظ است</div>
  </footer>;
}
