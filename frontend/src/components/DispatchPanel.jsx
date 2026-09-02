import { useEffect, useState } from "react";

import {
  getDispatches,
  createDispatch,
  updateDispatchStatus,
  cancelDispatch,
} from "../api/dispatches";

import { getEmergencies } from "../api/emergencies";

import { useWebSocket } from "../hooks/useWebSocket";


function DispatchPanel() {
  const [dispatches, setDispatches] = useState([]);
  const [emergencies, setEmergencies] = useState([]);

  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);

  const [selectedIncident, setSelectedIncident] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");


  // =====================================
  // LOAD DISPATCHES
  // =====================================

  async function loadDispatches() {
    try {
      const data = await getDispatches();

      console.log("[DISPATCHES]", data);

      setDispatches(
        Array.isArray(data)
          ? data
          : []
      );

    } catch (err) {

      console.error(
        "Failed to load dispatches:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to load dispatches."
      );
    }
  }


  // =====================================
  // LOAD EMERGENCIES
  // =====================================

  async function loadEmergencies() {
    try {

      const data =
        await getEmergencies();

      console.log(
        "[DISPATCH EMERGENCIES]",
        data
      );

      setEmergencies(
        Array.isArray(data)
          ? data
          : []
      );

    } catch (err) {

      console.error(
        "Failed to load emergencies:",
        err
      );

    }
  }


  // =====================================
  // INITIAL LOAD
  // =====================================

  useEffect(() => {

    async function loadData() {

      setLoading(true);

      await Promise.all([
        loadDispatches(),
        loadEmergencies(),
      ]);

      setLoading(false);
    }

    loadData();

  }, []);


  // =====================================
  // WEBSOCKET
  // =====================================

  useWebSocket((payload) => {

    console.log(
      "[DISPATCH EVENT]",
      payload
    );


    // -------------------------------------
    // CREATED
    // -------------------------------------

    if (
      payload.event ===
      "DISPATCH_CREATED"
    ) {

      loadDispatches();

      setSuccess(
        "Dispatch created successfully."
      );

      setTimeout(() => {
        setSuccess("");
      }, 3000);
    }


    // -------------------------------------
    // UPDATED
    // -------------------------------------

    if (
      payload.event === "DISPATCH_UPDATED" ||
      payload.event === "DISPATCH_STATUS_UPDATED"
    ) {

      loadDispatches();

    }


    // -------------------------------------
    // CANCELLED
    // -------------------------------------

    if (
      payload.event ===
      "DISPATCH_CANCELLED"
    ) {

      loadDispatches();

    }

  });


  // =====================================
  // CREATE DISPATCH
  // =====================================

  async function handleCreateDispatch(e) {

    e.preventDefault();

    setError("");
    setSuccess("");


    if (!selectedIncident) {

      setError(
        "Please select an emergency."
      );

      return;
    }


    try {

      setCreating(true);


      const token =
        localStorage.getItem(
          "access_token"
        );


      /*
       * Decode JWT payload to get
       * current user's ID.
       *
       * This avoids asking the user
       * to manually enter dispatcher_id.
       */

      let dispatcherId = null;


      if (token) {

        try {

          const payload =
            JSON.parse(
              atob(
                token.split(".")[1]
              )
            );

          dispatcherId =
            payload.sub ??
            payload.user_id ??
            payload.id;

        } catch (decodeError) {

          console.error(
            "Could not decode access token:",
            decodeError
          );

        }

      }


      if (!dispatcherId) {

        setError(
          "Unable to determine dispatcher ID from login session."
        );

        return;
      }


      const created =
        await createDispatch({
          incident_id:
            selectedIncident,

          dispatcher_id:
            dispatcherId,

          status: "CREATED",
        });


      console.log(
        "[DISPATCH CREATED]",
        created
      );


      setSuccess(
        "Dispatch created successfully."
      );

      setSelectedIncident("");


      await loadDispatches();


      setTimeout(() => {
        setSuccess("");
      }, 3000);


    } catch (err) {

      console.error(
        "Failed to create dispatch:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to create dispatch."
      );

    } finally {

      setCreating(false);

    }

  }


  // =====================================
  // STATUS UPDATE
  // =====================================

  async function handleStatusChange(
    dispatchId,
    newStatus
  ) {

    try {

      setActionLoading(dispatchId);
      setError("");

      await updateDispatchStatus(
        dispatchId,
        newStatus
      );

      await loadDispatches();

    } catch (err) {

      console.error(
        "Failed to update dispatch:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to update dispatch status."
      );

    } finally {

      setActionLoading(null);

    }

  }


  // =====================================
  // CANCEL
  // =====================================

  async function handleCancel(
    dispatchId
  ) {

    try {

      setActionLoading(dispatchId);
      setError("");

      await cancelDispatch(
        dispatchId
      );

      await loadDispatches();

    } catch (err) {

      console.error(
        "Failed to cancel dispatch:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to cancel dispatch."
      );

    } finally {

      setActionLoading(null);

    }

  }


  // =====================================
  // LOADING
  // =====================================

  if (loading) {

    return (
      <div className="dispatch-panel">

        <div className="empty-events">
          Loading dispatches...
        </div>

      </div>
    );

  }


  // =====================================
  // UI
  // =====================================

  return (

    <div className="dispatch-panel">


      {/* =================================
          HEADER
      ================================= */}

      <div className="panel-header">

        <div>

          <p className="eyebrow">
            RESPONSE OPERATIONS
          </p>

          <h3>
            Dispatch Management
          </h3>

        </div>


        <span className="live-label">

          <span className="status-dot"></span>

          LIVE

        </span>

      </div>


      {/* =================================
          CREATE DISPATCH
      ================================= */}

      <form
        onSubmit={handleCreateDispatch}
        className="dispatch-create-form"
      >

        <div>

          <label>
            Emergency / Incident
          </label>

          <select
            value={selectedIncident}
            onChange={(e) =>
              setSelectedIncident(
                e.target.value
              )
            }
          >

            <option value="">
              Select emergency
            </option>


            {emergencies.map(
              (emergency) => {

                const id =
                  emergency.id;

                return (
                  <option
                    key={id}
                    value={id}
                  >
                    Emergency{" "}
                    {String(id).slice(0, 8)}
                    ...
                    {emergency.severity
                      ? ` · ${emergency.severity}`
                      : ""}
                  </option>
                );

              }
            )}

          </select>

        </div>


        <button
          type="submit"
          disabled={creating}
        >
          {creating
            ? "Creating..."
            : "Create Dispatch"}
        </button>

      </form>


      {/* =================================
          SUCCESS
      ================================= */}

      {success && (
        <div className="dispatch-success">
          {success}
        </div>
      )}


      {/* =================================
          ERROR
      ================================= */}

      {error && (
        <div className="dispatch-error">
          {error}
        </div>
      )}


      {/* =================================
          DISPATCH LIST
      ================================= */}

      {dispatches.length === 0 ? (

        <div className="empty-events">

          <span className="status-dot"></span>

          No dispatches found.

        </div>

      ) : (

        <div className="dispatch-list">

          {dispatches.map(
            (dispatch) => {

              const dispatchId =
                dispatch.id;

              const status =
                dispatch.status ??
                "UNKNOWN";


              return (

                <div
                  className="dispatch-row"
                  key={dispatchId}
                >


                  {/* =======================
                      INFORMATION
                  ======================= */}

                  <div className="dispatch-info">

                    <strong>
                      Dispatch
                    </strong>

                    <span>
                      ID:{" "}
                      {String(
                        dispatchId
                      ).slice(0, 8)}
                      ...
                    </span>

                    <span>
                      Incident:{" "}
                      {dispatch.incident_id
                        ? String(
                            dispatch.incident_id
                          ).slice(0, 8)
                        : "N/A"}
                    </span>

                    <span>
                      Dispatcher:{" "}
                      {dispatch.dispatcher_id
                        ? String(
                            dispatch.dispatcher_id
                          ).slice(0, 8)
                        : "N/A"}
                    </span>

                  </div>


                  {/* =======================
                      STATUS
                  ======================= */}

                  <div className="dispatch-status">

                    <span className="dispatch-status-value">
                      {status}
                    </span>

                  </div>


                  {/* =======================
                      ACTIONS
                  ======================= */}

                  <div className="dispatch-actions">

                    {status !== "COMPLETED" &&
                     status !== "CANCELLED" && (

                      <select
                        value={status}
                        disabled={
                          actionLoading ===
                          dispatchId
                        }
                        onChange={(e) =>
                          handleStatusChange(
                            dispatchId,
                            e.target.value
                          )
                        }
                      >

                        <option value={status}>
                          Change status
                        </option>

                        <option value="CREATED">
                          CREATED
                        </option>

                        <option value="DISPATCHED">
                          DISPATCHED
                        </option>

                        <option value="EN_ROUTE">
                          EN_ROUTE
                        </option>

                        <option value="ARRIVED">
                          ARRIVED
                        </option>

                        <option value="TRANSPORTING">
                          TRANSPORTING
                        </option>

                        <option value="COMPLETED">
                          COMPLETED
                        </option>

                      </select>

                    )}


                    {status !== "COMPLETED" &&
                     status !== "CANCELLED" && (

                      <button
                        type="button"
                        disabled={
                          actionLoading ===
                          dispatchId
                        }
                        onClick={() =>
                          handleCancel(
                            dispatchId
                          )
                        }
                      >

                        {actionLoading ===
                        dispatchId
                          ? "..."
                          : "Cancel"}

                      </button>

                    )}

                  </div>

                </div>

              );

            }
          )}

        </div>

      )}

    </div>

  );
}


export default DispatchPanel;