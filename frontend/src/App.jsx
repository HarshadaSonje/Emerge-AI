import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";
import {
  Activity, Ambulance as AmbulanceIcon, Brain, Building2, CarFront, ChevronRight,
  ClipboardList, FileBarChart, Gauge, Hospital, LogOut, MapPin, Menu, RefreshCw,
  ShieldAlert, Siren, Users, X, Zap
} from "lucide-react";
import Login from "./pages/Login";
import { getCurrentUser, logout } from "./api/auth";
import { getDashboardOverview, getRecentEmergencies, getAmbulanceStatus, getEmergencyTrends } from "./api/dashboard";
import { getAmbulances, updateAmbulanceStatus, activateAmbulance, deactivateAmbulance, updateAmbulanceLocation } from "./api/ambulances";
import { getEmergencies, updateEmergencyStatus, updateEmergencySeverity, closeEmergency } from "./api/emergencies";
import { getDispatches, updateDispatchStatus, cancelDispatch } from "./api/dispatches";
import { getAssignments, updateAssignmentStatus } from "./api/assignments";
import { getHospitals, activateHospital, deactivateHospital } from "./api/hospitals";
import { getDrivers, updateDriverAvailability, activateDriver, deactivateDriver } from "./api/drivers";
import { getDailyReport, getAmbulanceUtilization, getDriverPerformance, getHospitalWorkload } from "./api/reports";
import { getTriageAssessment, getRecommendation, autoDispatch } from "./api/ai";
import ResponseMap from "./components/ResponseMap";
import { useWebSocket } from "./hooks/useWebSocket";

const emergencyStatuses = ["REPORTED","VERIFIED","DISPATCHED","AMBULANCE_ARRIVED","PATIENT_PICKED","HOSPITAL_ASSIGNED","COMPLETED","CANCELLED"];
const severities = ["LOW","MEDIUM","HIGH","CRITICAL"];
const ambulanceStatuses = ["AVAILABLE","DISPATCHED","ON_ROUTE","AT_SCENE","TRANSPORTING","AT_HOSPITAL","MAINTENANCE","OUT_OF_SERVICE"];
const dispatchStatuses = ["CREATED","ACCEPTED","EN_ROUTE","COMPLETED","CANCELLED"];
const assignmentStatuses = ["ASSIGNED","ACCEPTED","EN_ROUTE","ARRIVED_AT_SCENE","PATIENT_ONBOARD","ARRIVED_AT_HOSPITAL","COMPLETED","CANCELLED"];

const safeList = data => Array.isArray(data) ? data : data?.items ?? [];
const shortId = value => value ? String(value).slice(0, 8).toUpperCase() : "—";
const errorText = error => error?.response?.data?.detail || error?.response?.data?.message || "Request failed. Check the backend logs.";
const tone = value => String(value || "").toLowerCase().replaceAll(" ", "-");
const today = () => new Date().toISOString().slice(0,10);

function StatCard({ icon: Icon, label, value, meta, accent }) {
  return <div className={`stat-card ${accent || ""}`}><div className="stat-icon"><Icon size={17}/></div><div className="stat-copy"><span>{label}</span><strong>{value ?? 0}</strong>{meta && <small>{meta}</small>}</div></div>;
}
function SectionHeader({ eyebrow, title, action }) { return <div className="section-header"><div><span className="eyebrow">{eyebrow}</span><h2>{title}</h2></div>{action}</div>; }
function Badge({ children }) { return <span className={`badge ${tone(children)}`}>{children}</span>; }
function Empty({ text = "No data available." }) { return <div className="empty"><Activity size={18}/><span>{text}</span></div>; }
function ErrorBox({ error }) { return error ? <div className="error-box">{error}</div> : null; }

function App() {
  const [user,setUser] = useState(null);
  const [loading,setLoading] = useState(true);
  const [page,setPage] = useState("dashboard");
  const [sidebarOpen,setSidebarOpen] = useState(false);
  const [dashboard,setDashboard] = useState(null);
  const [ambulances,setAmbulances] = useState([]);
  const [emergencies,setEmergencies] = useState([]);
  const [dispatches,setDispatches] = useState([]);
  const [assignments,setAssignments] = useState([]);
  const [hospitals,setHospitals] = useState([]);
  const [drivers,setDrivers] = useState([]);
  const [events,setEvents] = useState([]);
  const [selectedEmergency,setSelectedEmergency] = useState(null);
  const [triage,setTriage] = useState(null);
  const [recommendation,setRecommendation] = useState(null);
  const [reports,setReports] = useState({daily:null,ambulances:[],drivers:[],hospitals:[]});
  const [reportDate,setReportDate] = useState(today());
  const [busy,setBusy] = useState("");
  const [error,setError] = useState("");
  const [activeSimulationAmbulanceId,setActiveSimulationAmbulanceId] = useState(null);

  const refreshDashboard = useCallback(async () => { try { setDashboard(await getDashboardOverview()); } catch(e) { console.error(e); } },[]);
  const loadAll = useCallback(async () => {
    setError("");
    try {
      const [d,a,e,ds,as,hs,dr] = await Promise.all([getDashboardOverview(),getAmbulances({page:1,limit:100}),getEmergencies({page:1,limit:100}),getDispatches({page:1,limit:100}),getAssignments({page:1,limit:100}),getHospitals({page:1,limit:100}),getDrivers({page:1,limit:100})]);
      setDashboard(d); setAmbulances(safeList(a)); setEmergencies(safeList(e)); setDispatches(safeList(ds)); setAssignments(safeList(as)); setHospitals(safeList(hs)); setDrivers(safeList(dr));
      setSelectedEmergency(cur => cur ? safeList(e).find(x=>String(x.id)===String(cur.id)) || cur : safeList(e)[0] || null);
    } catch(e) { setError(errorText(e)); }
  },[]);

  useEffect(() => { (async()=>{ try { const token=localStorage.getItem("access_token"); if(!token) return; setUser(await getCurrentUser()); } catch { localStorage.removeItem("access_token"); } finally { setLoading(false); } })(); },[]);
  useEffect(() => { if(user) loadAll(); },[user,loadAll]);

  const handleEvent = useCallback(payload => {
    if(!payload?.event) return;
    const d=payload.data || {};
    const labels={AMBULANCE_LOCATION_UPDATED:"Ambulance location updated",AMBULANCE_STATUS_UPDATED:"Ambulance status changed",EMERGENCY_STATUS_UPDATED:"Emergency status changed",EMERGENCY_CREATED:"Emergency created",EMERGENCY_UPDATED:"Emergency updated",EMERGENCY_RESOLVED:"Emergency resolved",DISPATCH_CREATED:"Dispatch created",DISPATCH_ASSIGNMENT_CREATED:"Dispatch assignment created",DISPATCH_ASSIGNMENT_STATUS_UPDATED:"Assignment status changed"};
    setEvents(cur=>[{id:Date.now()+Math.random(),label:labels[payload.event]||payload.event,data:d,time:new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit",second:"2-digit"})},...cur].slice(0,12));
    if(payload.event === "AMBULANCE_LOCATION_UPDATED") setAmbulances(cur=>cur.map(a=>String(a.id)===String(d.ambulance_id)?{...a,current_latitude:d.latitude,current_longitude:d.longitude}:a));
    if(payload.event === "AMBULANCE_STATUS_UPDATED") setAmbulances(cur=>cur.map(a=>String(a.id)===String(d.ambulance_id)?{...a,status:d.status}:a));
    if(payload.event === "EMERGENCY_STATUS_UPDATED") setEmergencies(cur=>cur.map(e=>String(e.id)===String(d.emergency_case_id)?{...e,status:d.status}:e));
    if(["EMERGENCY_CREATED","EMERGENCY_UPDATED","EMERGENCY_RESOLVED","DISPATCH_CREATED","DISPATCH_ASSIGNMENT_CREATED"].includes(payload.event)) loadAll();
    if(["AMBULANCE_STATUS_UPDATED","EMERGENCY_STATUS_UPDATED","DISPATCH_CREATED","DISPATCH_ASSIGNMENT_CREATED"].includes(payload.event)) refreshDashboard();
  },[loadAll,refreshDashboard]);
  const {connected}=useWebSocket(handleEvent);

  const action = async (key, fn, after=loadAll) => { try { setBusy(key); setError(""); await fn(); if(after) await after(); } catch(e) { setError(errorText(e)); } finally { setBusy(""); } };

  const selectEmergency = e => { setSelectedEmergency(e); setTriage(null); setRecommendation(null); };
  const runTriage = () => selectedEmergency && action("triage",async()=>setTriage(await getTriageAssessment(selectedEmergency.id)),null);
  const runRecommendation = () => selectedEmergency && action("recommendation",async()=>setRecommendation(await getRecommendation(selectedEmergency.id)),null);
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

  const simulateAmbulanceJourney = async (dispatchResult, emergency) => {
    const ambulanceId = dispatchResult?.ambulance_id;
    setActiveSimulationAmbulanceId(ambulanceId || null);
    const assignmentId = dispatchResult?.assignment_id;
    if (!ambulanceId || !assignmentId || !emergency) return;

    const ambulance = ambulances.find(a => String(a.id) === String(ambulanceId));
    if (!ambulance) return;

    const startLat = Number(ambulance.current_latitude ?? ambulance.latitude);
    const startLng = Number(ambulance.current_longitude ?? ambulance.longitude);
    const endLat = Number(emergency.latitude);
    const endLng = Number(emergency.longitude);
    if (![startLat, startLng, endLat, endLng].every(Number.isFinite)) return;

    try {
      // Demonstration lifecycle: assignment is accepted, goes en route,
      // streams location updates to the emergency, then arrives at scene.
      await updateAssignmentStatus(assignmentId, "ACCEPTED");
      await sleep(700);
      await updateAssignmentStatus(assignmentId, "EN_ROUTE");

      const steps = 14;
      for (let step = 1; step <= steps; step += 1) {
        const t = step / steps;
        const eased = t * t * (3 - 2 * t);
        const latitude = startLat + (endLat - startLat) * eased;
        const longitude = startLng + (endLng - startLng) * eased;

        setAmbulances(current => current.map(item =>
          String(item.id) === String(ambulanceId)
            ? { ...item, current_latitude: latitude, current_longitude: longitude, status: "ON_ROUTE" }
            : item
        ));

        await updateAmbulanceLocation(ambulanceId, latitude, longitude);
        await sleep(750);
      }

      await updateAssignmentStatus(assignmentId, "ARRIVED_AT_SCENE");
      await loadAll();
    } catch (simulationError) {
      console.error("Ambulance simulation failed:", simulationError);
      setError(errorText(simulationError));
    }
  };

  const runAutoDispatch = () => selectedEmergency && action(
    "auto-dispatch",
    async () => {
      const dispatchResult = await autoDispatch(selectedEmergency.id);
      await loadAll();
      // Option A: demo simulation. It uses the real APIs, so the database,
      // WebSocket stream and map stay synchronized while the marker moves.
      void simulateAmbulanceJourney(dispatchResult, selectedEmergency);
    },
    null,
  );

  const loadReports = async () => { try { setBusy("reports"); setError(""); const [daily,ambulancesR,driversR,hospitalsR]=await Promise.all([getDailyReport(reportDate),getAmbulanceUtilization(),getDriverPerformance(),getHospitalWorkload()]); setReports({daily,ambulances:ambulancesR,drivers:driversR,hospitals:hospitalsR}); } catch(e) { setError(errorText(e)); } finally { setBusy(""); } };
  useEffect(()=>{ if(user && page==="reports") loadReports(); },[user,page]);

  const counts = dashboard || {};
  const nav = [
    ["dashboard","Command Center",Gauge],["emergencies","Emergencies",Siren],["ambulances","Ambulances",AmbulanceIcon],["dispatches","Dispatches",Zap],["hospitals","Hospitals",Building2],["drivers","Drivers",Users],["reports","Reports",FileBarChart],["ai","AI Operations",Brain]
  ];

  if(loading) return <div className="loading-screen"><div className="brand-mark">E</div><span>Initializing command center…</span></div>;
  if(!user) return <Login onLogin={async()=>{setUser(await getCurrentUser());}}/>;

  return <div className="app-shell">
    <aside className={`sidebar ${sidebarOpen?"open":""}`}>
      <div className="sidebar-brand"><div className="brand-mark">E</div><div><strong>EMERGE-AI</strong><span>Emergency Intelligence</span></div><button className="mobile-close" onClick={()=>setSidebarOpen(false)}><X size={18}/></button></div>
      <div className="sidebar-section"><span className="sidebar-label">OPERATIONS</span>{nav.map(([id,label,Icon])=><button key={id} className={page===id?"nav-item active":"nav-item"} onClick={()=>{setPage(id);setSidebarOpen(false)}}><Icon size={17}/><span>{label}</span>{page===id&&<ChevronRight size={14}/>}</button>)}</div>
      <div className="sidebar-bottom"><div className="connection"><i className={connected?"online":""}/><div><strong>{connected?"LIVE CONNECTION":"RECONNECTING"}</strong><span>Real-time event stream</span></div></div><button className="logout" onClick={()=>{logout();setUser(null)}}><LogOut size={16}/> Sign out</button></div>
    </aside>
    {sidebarOpen&&<div className="overlay" onClick={()=>setSidebarOpen(false)}/>} 
    <main className="main-area">
      <header className="topbar"><button className="menu-btn" onClick={()=>setSidebarOpen(true)}><Menu size={20}/></button><div><span className="top-eyebrow">EMERGENCY RESPONSE PLATFORM</span><h1>{nav.find(x=>x[0]===page)?.[1] || "Command Center"}</h1></div><div className="top-actions"><div className="system-pill"><i className={connected?"online":""}/>{connected?"SYSTEM ONLINE":"CONNECTING"}</div><div className="user-chip"><span>{user.full_name?.[0] || user.email?.[0] || "U"}</span><div><strong>{user.full_name || user.email}</strong><small>{user.role || "Operator"}</small></div></div></div></header>
      <div className="content">
        <ErrorBox error={error}/>
        {page==="dashboard" && <Dashboard dashboard={counts} emergencies={emergencies} ambulances={ambulances} events={events} connected={connected} selectedEmergency={selectedEmergency} activeAmbulanceId={activeSimulationAmbulanceId} setSelectedEmergency={selectEmergency} refresh={loadAll}/>} 
        {page==="emergencies" && <EmergenciesPage emergencies={emergencies} selected={selectedEmergency} select={selectEmergency} busy={busy} action={action} setEmergencies={setEmergencies} setSelected={setSelectedEmergency} runTriage={runTriage} runRecommendation={runRecommendation} runAutoDispatch={runAutoDispatch} triage={triage} recommendation={recommendation}/>} 
        {page==="ambulances" && <AmbulancesPage ambulances={ambulances} busy={busy} action={action}/>} 
        {page==="dispatches" && <DispatchesPage dispatches={dispatches} assignments={assignments} busy={busy} action={action}/>} 
        {page==="hospitals" && <HospitalsPage hospitals={hospitals} busy={busy} action={action}/>} 
        {page==="drivers" && <DriversPage drivers={drivers} ambulances={ambulances} busy={busy} action={action}/>} 
        {page==="reports" && <ReportsPage reports={reports} date={reportDate} setDate={setReportDate} reload={loadReports} busy={busy}/>} 
        {page==="ai" && <AIPage emergencies={emergencies} selected={selectedEmergency} select={selectEmergency} triage={triage} recommendation={recommendation} busy={busy} runTriage={runTriage} runRecommendation={runRecommendation} runAutoDispatch={runAutoDispatch}/>} 
      </div>
    </main>
  </div>;
}

function Dashboard({dashboard:d,emergencies,ambulances,events,connected,selectedEmergency,activeAmbulanceId,setSelectedEmergency,refresh}) {
  return <div className="page-stack">
    <div className="hero-row"><div><span className="eyebrow">COMMAND CENTER</span><h2>Emergency operations at a glance</h2><p>Monitor incidents, fleet readiness and response activity in real time.</p></div><button className="btn ghost" onClick={refresh}><RefreshCw size={15}/> Refresh</button></div>
    <div className="stats-grid"><StatCard icon={ShieldAlert} label="Active emergencies" value={d.active_emergencies} meta={`${d.completed_emergencies||0} completed`} accent="red"/><StatCard icon={AmbulanceIcon} label="Available ambulances" value={d.available_ambulances} meta={`${d.busy_ambulances||0} currently busy`} accent="blue"/><StatCard icon={Zap} label="Active dispatches" value={d.active_dispatches} meta={`${d.completed_dispatches||0} completed`} accent="amber"/><StatCard icon={Hospital} label="Hospitals" value={d.total_hospitals} meta={`${d.total_departments||0} departments`} accent="green"/></div>
    <div className="map-events-grid"><section className="panel map-panel"><SectionHeader eyebrow="LIVE OPERATIONS" title="Response map" action={<span className="live-chip"><i className={connected?"online":""}/>{connected?"LIVE":"OFFLINE"}</span>}/><div className="map-wrap"><ResponseMap emergencies={emergencies} ambulances={ambulances} selectedEmergency={selectedEmergency} activeAmbulanceId={activeAmbulanceId}/></div></section><section className="panel"><SectionHeader eyebrow="REAL-TIME" title="Operations activity" action={<span className="muted">{events.length} recent</span>}/><div className="events-list">{events.length?events.map(e=><div className="event" key={e.id}><div className="event-icon"><Activity size={14}/></div><div><strong>{e.label}</strong><span>{eventSummary(e.data)}</span></div><time>{e.time}</time></div>):<Empty text="Waiting for live operations events"/>}</div></section></div>
    <section className="panel"><SectionHeader eyebrow="EMERGENCY MANAGEMENT" title="Active cases" action={<span className="muted">{emergencies.length} loaded</span>}/><div className="case-grid">{emergencies.length?emergencies.slice(0,8).map(e=><button className={`case-card ${selectedEmergency?.id===e.id?"selected":""}`} key={e.id} onClick={()=>setSelectedEmergency(e)}><div className="case-top"><strong>{e.case_number}</strong><Badge>{e.severity}</Badge></div><span>{e.incident_type}</span><small>{e.address}</small><div className="case-bottom"><Badge>{e.status}</Badge><span>{e.patient_name||"Patient not provided"}</span></div></button>):<Empty text="No emergency cases found"/>}</div></section>
    <section className="panel"><SectionHeader eyebrow="NETWORK STATUS" title="System overview"/><div className="mini-grid"><div><span>Total ambulances</span><strong>{d.total_ambulances||0}</strong></div><div><span>Maintenance</span><strong>{d.maintenance_ambulances||0}</strong></div><div><span>Drivers</span><strong>{d.total_drivers||0}</strong></div><div><span>Available drivers</span><strong>{d.available_drivers||0}</strong></div><div><span>Active cases</span><strong>{d.active_emergencies||0}</strong></div><div><span>Departments</span><strong>{d.total_departments||0}</strong></div></div></section>
  </div>;
}
function eventSummary(d){ if(!d||!Object.keys(d).length) return "System event received"; if(d.ambulance_id) return `Ambulance ${shortId(d.ambulance_id)}${d.status?` · ${d.status}`:""}`; if(d.emergency_case_id) return `Emergency ${shortId(d.emergency_case_id)}${d.status?` · ${d.status}`:""}`; if(d.dispatch_id) return `Dispatch ${shortId(d.dispatch_id)}`; return "Operational update received"; }

function EmergenciesPage({emergencies,selected,select,busy,action,setEmergencies,setSelected,runTriage,runRecommendation,runAutoDispatch,triage,recommendation}) {
 return <div className="page-stack"><SectionHeader eyebrow="EMERGENCY MANAGEMENT" title="Emergency cases" action={<span className="muted">{emergencies.length} cases</span>}/><div className="two-pane"><div className="list-panel">{emergencies.length?emergencies.map(e=><button className={`list-row ${selected?.id===e.id?"selected":""}`} key={e.id} onClick={()=>select(e)}><div><strong>{e.case_number}</strong><span>{e.incident_type} · {e.address}</span></div><div><Badge>{e.severity}</Badge><Badge>{e.status}</Badge></div></button>):<Empty text="No emergency cases"/>}</div><div className="detail-panel">{!selected?<Empty text="Select an emergency case"/>:<><div className="detail-title"><div><span className="eyebrow">CASE {selected.case_number}</span><h2>{selected.incident_type}</h2></div><Badge>{selected.severity}</Badge></div><div className="detail-grid"><Info label="Status" value={selected.status}/><Info label="Reporter" value={selected.reporter_name}/><Info label="Phone" value={selected.reporter_phone}/><Info label="Patient" value={selected.patient_name||"Not provided"}/><Info label="Age" value={selected.patient_age??"—"}/><Info label="Gender" value={selected.patient_gender||"—"}/><Info label="Address" value={selected.address}/><Info label="Coordinates" value={`${Number(selected.latitude).toFixed(5)}, ${Number(selected.longitude).toFixed(5)}`}/></div><div className="description"><span>Description</span><p>{selected.description}</p></div><div className="action-groups"><ActionGroup title="Status">{emergencyStatuses.map(s=><button key={s} disabled={busy||selected.status===s} onClick={()=>action(`e-status-${s}`,async()=>{const u=await updateEmergencyStatus(selected.id,s);setEmergencies(c=>c.map(x=>x.id===u.id?u:x));setSelected(u)})}>{s}</button>)}</ActionGroup><ActionGroup title="Severity">{severities.map(s=><button key={s} disabled={busy||selected.severity===s} onClick={()=>action(`e-sev-${s}`,async()=>{const u=await updateEmergencySeverity(selected.id,s);setEmergencies(c=>c.map(x=>x.id===u.id?u:x));setSelected(u)})}>{s}</button>)}</ActionGroup><ActionGroup title="AI & response"><button className="primary" disabled={busy} onClick={runTriage}>{busy==="triage"?"Assessing…":"AI Triage"}</button><button className="primary" disabled={busy} onClick={runRecommendation}>{busy==="recommendation"?"Calculating…":"Get Recommendation"}</button><button className="danger" disabled={busy} onClick={runAutoDispatch}>{busy==="auto-dispatch"?"Dispatching…":"Auto Dispatch"}</button><button disabled={busy||!selected.is_active} onClick={()=>action("close",async()=>{const u=await closeEmergency(selected.id);setEmergencies(c=>c.map(x=>x.id===u.id?u:x));setSelected(u)})}>Close case</button></ActionGroup></div>{(triage||recommendation)&&<div className="ai-results">{triage&&<div className="ai-card"><div className="ai-title"><Brain size={17}/> AI triage assessment</div><div className="ai-grid"><Info label="Urgency" value={triage.urgency}/><Info label="Priority" value={triage.recommended_priority}/><Info label="Department" value={triage.recommended_department}/><Info label="Immediate attention" value={triage.immediate_attention?"YES":"NO"}/></div><p>{triage.reasoning}</p></div>}{recommendation&&<div className="ai-card"><div className="ai-title"><Zap size={17}/> Dispatch recommendation</div><div className="ai-grid"><Info label="Ambulance" value={shortId(recommendation.ambulance_id)}/><Info label="Driver" value={shortId(recommendation.driver_id)}/><Info label="Hospital" value={shortId(recommendation.hospital_id)}/><Info label="Distance" value={`${Number(recommendation.distance_km).toFixed(2)} km`}/><Info label="Priority score" value={recommendation.priority_score}/></div></div>}</div>}</>}</div></div></div>;
}
function Info({label,value}){return <div className="info"><span>{label}</span><strong>{String(value??"—")}</strong></div>}
function ActionGroup({title,children}){return <div className="action-group"><span>{title}</span><div className="button-wrap">{children}</div></div>}

function AmbulancesPage({ambulances,busy,action}){return <div className="page-stack"><SectionHeader eyebrow="FLEET OPERATIONS" title="Ambulance network" action={<span className="muted">{ambulances.length} vehicles</span>}/><div className="table-panel"><table><thead><tr><th>Vehicle</th><th>Type</th><th>Status</th><th>Location</th><th>Active</th><th>Actions</th></tr></thead><tbody>{ambulances.map(a=><tr key={a.id}><td><strong>{a.vehicle_number}</strong><small>{a.registration_number}</small></td><td>{a.vehicle_type}</td><td><Badge>{a.status}</Badge></td><td>{a.current_latitude!=null?`${Number(a.current_latitude).toFixed(4)}, ${Number(a.current_longitude).toFixed(4)}`:"No location"}</td><td>{a.is_active?"YES":"NO"}</td><td><div className="row-actions"><select value={a.status} disabled={busy===`a-status-${a.id}`} onChange={e=>action(`a-status-${a.id}`,()=>updateAmbulanceStatus(a.id,e.target.value))}>{ambulanceStatuses.map(s=><option key={s}>{s}</option>)}</select><button disabled={busy} onClick={()=>action(`a-toggle-${a.id}`,()=>a.is_active?deactivateAmbulance(a.id):activateAmbulance(a.id))}>{a.is_active?"Deactivate":"Activate"}</button>{a.current_latitude!=null&&<button disabled={busy} onClick={()=>{const lat=Number(a.current_latitude)+0.001; const lng=Number(a.current_longitude)+0.001; action(`a-move-${a.id}`,()=>updateAmbulanceLocation(a.id,lat,lng))}}>Move +</button>}</div></td></tr>)}</tbody></table>{!ambulances.length&&<Empty text="No ambulances found"/>}</div></div>}

function DispatchesPage({dispatches,assignments,busy,action}){return <div className="page-stack"><SectionHeader eyebrow="RESPONSE OPERATIONS" title="Dispatches & assignments"/><div className="table-panel"><table><thead><tr><th>Dispatch</th><th>Incident</th><th>Dispatcher</th><th>Status</th><th>Actions</th></tr></thead><tbody>{dispatches.map(d=><tr key={d.id}><td><strong>{shortId(d.id)}</strong><small>{new Date(d.assigned_at||d.created_at).toLocaleString()}</small></td><td>{shortId(d.incident_id)}</td><td>{shortId(d.dispatcher_id)}</td><td><Badge>{d.status}</Badge></td><td><div className="row-actions"><select value={d.status} disabled={busy} onChange={e=>action(`d-${d.id}`,()=>updateDispatchStatus(d.id,e.target.value))}>{dispatchStatuses.map(s=><option key={s}>{s}</option>)}</select><button disabled={busy||["COMPLETED","CANCELLED"].includes(d.status)} onClick={()=>action(`dc-${d.id}`,()=>cancelDispatch(d.id))}>Cancel</button></div></td></tr>)}</tbody></table>{!dispatches.length&&<Empty text="No dispatches found"/>}</div><section className="panel"><SectionHeader eyebrow="FIELD ASSIGNMENTS" title="Dispatch assignments" action={<span className="muted">{assignments.length} assignments</span>}/><div className="assignment-grid">{assignments.map(a=><div className="assignment" key={a.id}><div><strong>{shortId(a.id)}</strong><span>Ambulance {shortId(a.ambulance_id)} · Driver {shortId(a.driver_id)}</span><small>Hospital {shortId(a.hospital_id)}</small></div><select value={a.status} disabled={busy} onChange={e=>action(`as-${a.id}`,()=>updateAssignmentStatus(a.id,e.target.value))}>{assignmentStatuses.map(s=><option key={s}>{s}</option>)}</select></div>)}{!assignments.length&&<Empty text="No assignments found"/>}</div></section></div>}

function HospitalsPage({hospitals,busy,action}){return <div className="page-stack"><SectionHeader eyebrow="HOSPITAL NETWORK" title="Hospitals" action={<span className="muted">{hospitals.length} facilities</span>}/><div className="hospital-grid">{hospitals.map(h=><div className="hospital-card" key={h.id}><div className="hospital-icon"><Hospital size={19}/></div><div className="hospital-main"><div className="case-top"><strong>{h.name}</strong><Badge>{h.is_active?"ACTIVE":"INACTIVE"}</Badge></div><span>{h.code}</span><p>{h.address}</p><small>{h.email} · {h.phone}</small></div><button disabled={busy} onClick={()=>action(`h-${h.id}`,()=>h.is_active?deactivateHospital(h.id):activateHospital(h.id))}>{h.is_active?"Deactivate":"Activate"}</button></div>)}{!hospitals.length&&<Empty text="No hospitals found"/>}</div></div>}

function DriversPage({drivers,busy,action}){return <div className="page-stack"><SectionHeader eyebrow="FIELD PERSONNEL" title="Drivers" action={<span className="muted">{drivers.length} drivers</span>}/><div className="table-panel"><table><thead><tr><th>Driver</th><th>License</th><th>Experience</th><th>Ambulance</th><th>Availability</th><th>Actions</th></tr></thead><tbody>{drivers.map(d=><tr key={d.id}><td><strong>{shortId(d.id)}</strong><small>User {shortId(d.user_id)}</small></td><td>{d.license_number}<small>Expiry {d.license_expiry}</small></td><td>{d.years_of_experience} yrs</td><td>{shortId(d.ambulance_id)}</td><td><Badge>{d.is_available?"AVAILABLE":"BUSY"}</Badge></td><td><div className="row-actions"><button disabled={busy} onClick={()=>action(`drv-${d.id}`,()=>updateDriverAvailability(d.id,!d.is_available))}>{d.is_available?"Set busy":"Set available"}</button><button disabled={busy} onClick={()=>action(`drva-${d.id}`,()=>d.is_active?deactivateDriver(d.id):activateDriver(d.id))}>{d.is_active?"Deactivate":"Activate"}</button></div></td></tr>)}</tbody></table>{!drivers.length&&<Empty text="No drivers found"/>}</div></div>}

function ReportsPage({reports,date,setDate,reload,busy}){return <div className="page-stack"><div className="hero-row"><div><span className="eyebrow">ANALYTICS</span><h2>Operational reports</h2><p>Use the reporting endpoints already provided by the backend.</p></div><div className="date-action"><input type="date" value={date} onChange={e=>setDate(e.target.value)}/><button className="btn primary" disabled={busy} onClick={reload}><RefreshCw size={15}/> Refresh report</button></div></div>{reports.daily&&<div className="stats-grid four"><StatCard icon={FileBarChart} label="Cases" value={reports.daily.total_cases} meta={reports.daily.date}/><StatCard icon={Activity} label="Active" value={reports.daily.active_cases}/><StatCard icon={Zap} label="Completed" value={reports.daily.completed_cases}/><StatCard icon={ShieldAlert} label="Critical" value={reports.daily.critical_cases} accent="red"/></div>}<ReportTable title="Ambulance utilization" columns={["Vehicle","Registration","Status","Dispatches"]} rows={reports.ambulances.map(r=>[`${r.vehicle_number}`,r.registration_number,r.status,r.dispatch_count])}/><ReportTable title="Driver performance" columns={["Driver","Experience","Availability","Dispatches"]} rows={reports.drivers.map(r=>[shortId(r.driver_id),`${r.years_of_experience} yrs`,r.is_available?"AVAILABLE":"BUSY",r.dispatch_count])}/><ReportTable title="Hospital workload" columns={["Hospital","Assignments"]} rows={reports.hospitals.map(r=>[r.hospital_name,r.total_assignments])}/></div>}
function ReportTable({title,columns,rows}){return <section className="panel"><SectionHeader eyebrow="REPORT" title={title}/><div className="table-panel inner"><table><thead><tr>{columns.map(c=><th key={c}>{c}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}>{r.map((v,j)=><td key={j}>{v}</td>)}</tr>)}</tbody></table>{!rows.length&&<Empty text="No report data"/>}</div></section>}

function AIPage({
  emergencies,
  selected,
  select,
  triage,
  recommendation,
  busy,
  runTriage,
  runRecommendation,
  runAutoDispatch,
}) {
  return (
    <div className="page-stack">
      <div className="hero-row">
        <div>
          <span className="eyebrow">AI OPERATIONS</span>
          <h2>Response intelligence</h2>
          <p>
            AI triage, dispatch recommendation and automatic dispatch are
            connected to the existing backend services.
          </p>
        </div>
        <div className="ai-status">
          <Brain size={18} /> AI READY
        </div>
      </div>

      <section className="panel">
        <SectionHeader eyebrow="CASE SELECTION" title="Select an emergency" />
        <div className="ai-case-list">
          {emergencies.map((e) => (
            <button
              className={selected?.id === e.id ? "selected" : ""}
              key={e.id}
              onClick={() => select(e)}
            >
              <div>
                <strong>{e.case_number}</strong>
                <span>
                  {e.incident_type} · {e.address}
                </span>
              </div>
              <Badge>{e.severity}</Badge>
            </button>
          ))}
        </div>
        {!emergencies.length && <Empty text="No emergencies available" />}
      </section>

      {selected && (
        <section className="ai-workspace">
          <div className="panel">
            <SectionHeader eyebrow={selected.case_number} title="AI tools" />
            <div className="ai-tool-buttons">
              <button
                className="primary"
                disabled={!!busy}
                onClick={runTriage}
              >
                <Brain size={16} />
                {busy === "triage" ? "Assessing…" : "Run AI triage"}
              </button>

              <button
                className="primary"
                disabled={!!busy}
                onClick={runRecommendation}
              >
                <Zap size={16} />
                {busy === "recommendation"
                  ? "Calculating…"
                  : "Recommend response"}
              </button>

              <button
                className="danger"
                disabled={!!busy}
                onClick={runAutoDispatch}
              >
                <Siren size={16} />
                {busy === "auto-dispatch" ? "Dispatching…" : "Auto dispatch"}
              </button>
            </div>
          </div>

          {(triage || recommendation) && (
            <div className="ai-result-grid">
              {triage && (
                <div className="ai-card">
                  <div className="ai-title">
                    <Brain size={17} /> Triage assessment
                  </div>
                  <Info label="Urgency" value={triage.urgency} />
                  <Info
                    label="Priority"
                    value={triage.recommended_priority}
                  />
                  <Info
                    label="Department"
                    value={triage.recommended_department}
                  />
                  <Info
                    label="Immediate attention"
                    value={triage.immediate_attention ? "YES" : "NO"}
                  />
                  <p>{triage.reasoning}</p>
                </div>
              )}

              {recommendation && (
                <div className="ai-card">
                  <div className="ai-title">
                    <Zap size={17} /> Dispatch recommendation
                  </div>
                  <Info
                    label="Ambulance"
                    value={shortId(recommendation.ambulance_id)}
                  />
                  <Info
                    label="Driver"
                    value={shortId(recommendation.driver_id)}
                  />
                  <Info
                    label="Hospital"
                    value={shortId(recommendation.hospital_id)}
                  />
                  <Info
                    label="Distance"
                    value={`${Number(recommendation.distance_km).toFixed(2)} km`}
                  />
                  <Info
                    label="Priority score"
                    value={recommendation.priority_score}
                  />
                </div>
              )}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default App;
