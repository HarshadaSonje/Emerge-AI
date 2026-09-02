import { useEffect, useMemo, useRef, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const CENTER = [18.5204, 73.8567];
const ambulanceIcon = new L.DivIcon({ className: "", html: '<div class="map-ambulance">🚑</div>', iconSize: [36,36], iconAnchor: [18,18] });
const emergencyIcon = new L.DivIcon({ className: "", html: '<div class="map-emergency">!</div>', iconSize: [34,34], iconAnchor: [17,17] });

function FitBounds({ points }) {
  const map = useMap();
  useEffect(() => {
    if (points.length > 1) map.fitBounds(points, { padding: [35,35], maxZoom: 14 });
    else if (points.length === 1) map.setView(points[0], 13);
  }, [map, points]);
  return null;
}

function AnimatedMarker({ ambulance }) {
  const lat = Number(ambulance.current_latitude ?? ambulance.latitude);
  const lng = Number(ambulance.current_longitude ?? ambulance.longitude);
  const [position, setPosition] = useState([lat,lng]);
  const from = useRef([lat,lng]);
  const to = useRef([lat,lng]);

  useEffect(() => {
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;
    const start = position;
    from.current = start;
    to.current = [lat,lng];
    const started = performance.now();
    let frame;
    const animate = now => {
      const t = Math.min((now-started)/900, 1);
      const eased = t*(2-t);
      setPosition([
        from.current[0] + (to.current[0]-from.current[0])*eased,
        from.current[1] + (to.current[1]-from.current[1])*eased,
      ]);
      if (t < 1) frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [lat,lng]);

  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  return <Marker position={position} icon={ambulanceIcon}>
    <Popup>
      <b>{ambulance.vehicle_number || ambulance.registration_number || "Ambulance"}</b><br/>
      {ambulance.vehicle_type || "—"} · {ambulance.status || "UNKNOWN"}<br/>
      {position[0].toFixed(5)}, {position[1].toFixed(5)}
    </Popup>
  </Marker>;
}

export default function ResponseMap({ emergencies = [], ambulances = [], selectedEmergency, activeAmbulanceId = null }) {
  const emergencyPoints = emergencies.map(e => [Number(e.latitude),Number(e.longitude)]).filter(p => p.every(Number.isFinite));
  const ambulancePoints = ambulances.map(a => [Number(a.current_latitude ?? a.latitude),Number(a.current_longitude ?? a.longitude)]).filter(p => p.every(Number.isFinite));
  const points = useMemo(() => [...emergencyPoints,...ambulancePoints], [emergencies,ambulances]);
  const selected = selectedEmergency ? [Number(selectedEmergency.latitude),Number(selectedEmergency.longitude)] : null;
  const activeAmbulance = activeAmbulanceId ? ambulances.find(a => String(a.id) === String(activeAmbulanceId)) : null;
  const activePoint = activeAmbulance ? [Number(activeAmbulance.current_latitude ?? activeAmbulance.latitude), Number(activeAmbulance.current_longitude ?? activeAmbulance.longitude)] : null;
  const line = selected && selected.every(Number.isFinite) && activePoint && activePoint.every(Number.isFinite) ? [activePoint,selected] : [];

  return <MapContainer center={CENTER} zoom={12} scrollWheelZoom style={{height:"100%",width:"100%"}}>
    <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    <FitBounds points={points}/>
    {emergencies.map(e => {
      const lat=Number(e.latitude), lng=Number(e.longitude); if(!Number.isFinite(lat)||!Number.isFinite(lng)) return null;
      return <Circle key={`zone-${e.id}`} center={[lat,lng]} radius={450} pathOptions={{className:"",color:"#ef4444",fillColor:"#ef4444",fillOpacity:.08}}>
        <Marker position={[lat,lng]} icon={emergencyIcon}><Popup><b>{e.case_number || "Emergency"}</b><br/>{e.incident_type || "—"} · {e.severity || "—"}<br/>{e.status || "—"}</Popup></Marker>
      </Circle>;
    })}
    {ambulances.map(a => <AnimatedMarker key={a.id} ambulance={a}/>)}
    {line.length === 2 && <Polyline positions={line} pathOptions={{dashArray:"8 8",opacity:.55}}/>}
  </MapContainer>;
}
