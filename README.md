
## Final deployment notes

This package intentionally excludes local dependencies and secrets. Before running:

1. Copy `backend/.env.example` to `backend/.env` and set deployment values.
2. Copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_URL` to the backend URL.
3. Install backend dependencies with `pip install -r backend/requirements.txt`.
4. Install frontend dependencies with `npm install` inside `frontend/`.
5. Run database migrations before starting the backend.

### Ambulance demo simulation

After Auto Dispatch succeeds, the frontend automatically demonstrates the dispatched ambulance journey to the selected emergency. The simulation uses the existing assignment-status and ambulance-location APIs, so the database and WebSocket map updates stay synchronized. It stops at `ARRIVED_AT_SCENE`; the remaining patient transport and completion lifecycle can continue through the normal assignment status controls.
