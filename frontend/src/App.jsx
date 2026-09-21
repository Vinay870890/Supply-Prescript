import "./App.css";
import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  Database,
  CircleDollarSign,
  Clock3,
  LayoutDashboard,
  RefreshCw,
  Settings,
  ShieldCheck,
  Target,
  Truck,
  Zap,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const API_BASE = "http://localhost:8001/api";

const formatPercent = (value) =>
  `${Number(value || 0).toFixed(1)}%`;

const formatCurrency = (value) =>
  `$${Number(value || 0).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

function App() {
  const [health, setHealth] = useState(null);
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [models, setModels] = useState([]);
  const [activeModel, setActiveModel] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activePage, setActivePage] = useState("Dashboard");

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);

    try {
      const [
        healthRes,
        summaryRes,
        historyRes,
        decisionsRes,
        modelsRes,
        activeModelRes,
      ] = await Promise.all([
        fetch(`${API_BASE}/health`),
        fetch(`${API_BASE}/evaluations/summary`),
        fetch(`${API_BASE}/evaluations/history`),
        fetch(`${API_BASE}/decisions`),
        fetch(`${API_BASE}/models`),
        fetch(`${API_BASE}/models/active`),
      ]);

      if (!healthRes.ok) {
        throw new Error("Backend health check failed");
      }

      if (!summaryRes.ok) {
        throw new Error("Evaluation summary unavailable");
      }

      if (!historyRes.ok) {
        throw new Error("Evaluation history unavailable");
      }

      if (!decisionsRes.ok) {
        throw new Error("Decision list unavailable");
      }

      if (!modelsRes.ok) {
        throw new Error("Model registry unavailable");
      }

      if (!activeModelRes.ok) {
        throw new Error("Active model unavailable");
      }

      const [
        h,
        s,
        hist,
        dec,
        modelData,
        activeModelData,
      ] = await Promise.all([
        healthRes.json(),
        summaryRes.json(),
        historyRes.json(),
        decisionsRes.json(),
        modelsRes.json(),
        activeModelRes.json(),
      ]);

      setHealth(h);
      setSummary(s);
      setHistory(hist.results || []);
      setDecisions(Array.isArray(dec) ? dec : dec.results || []);
      setModels(modelData.models || []);
      setActiveModel(activeModelData.model || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const actionData = useMemo(() => {
    const counts = {};

    history.forEach((item) => {
      counts[item.selected_action] =
        (counts[item.selected_action] || 0) + 1;
    });

    return Object.entries(counts).map(([name, value]) => ({
      name,
      value,
    }));
  }, [history]);

  // Analytics uses the clean real-data batch created for validation:
  // decision IDs 45-64. Dashboard/Decisions/Outcomes continue to use
  // the complete history returned by the backend.
  const cleanBatchHistory = useMemo(
    () =>
      history
        .filter(
          (item) =>
            Number(item.decision_id) >= 45 &&
            Number(item.decision_id) <= 64
        )
        .sort(
          (a, b) =>
            Number(a.decision_id) - Number(b.decision_id)
        ),
    [history]
  );

  const cleanBatchPerformanceData = useMemo(
    () =>
      cleanBatchHistory.map((item) => ({
        name: `#${item.decision_id}`,
        predicted: Number(
          (Number(item.predicted_delay_probability) * 100).toFixed(2)
        ),
        actual: item.actual_delay_flag ? 100 : 0,
        shipment: item.shipment_id,
        outcome: item.outcome_status,
      })),
    [cleanBatchHistory]
  );
    const cleanBatchActionData = useMemo(() => {
    const counts = {};

    cleanBatchHistory.forEach((item) => {
      counts[item.selected_action] =
        (counts[item.selected_action] || 0) + 1;
    });

    return Object.entries(counts).map(([name, value]) => ({
      name,
      value,
    }));
  }, [cleanBatchHistory]);

  const cleanBatchSummary = useMemo(() => {
    const evaluated = cleanBatchHistory.length;

    const correctPredictions = cleanBatchHistory.filter(
      (item) => item.prediction_correct === true
    ).length;

    const successfulDecisions = cleanBatchHistory.filter(
      (item) => item.decision_success === true
    ).length;

    const onTimeShipments = cleanBatchHistory.filter(
      (item) => item.actual_delay_flag === 0
    ).length;

    const delayedShipments = cleanBatchHistory.filter(
      (item) => item.actual_delay_flag === 1
    ).length;

    const totalSavings = cleanBatchHistory.reduce(
      (sum, item) =>
        sum + Number(item.estimated_savings_usd || 0),
      0
    );

    const averageCostVariance =
      evaluated > 0
        ? cleanBatchHistory.reduce(
            (sum, item) =>
              sum + Number(item.cost_variance_usd || 0),
            0
          ) / evaluated
        : 0;

    const averageRoi =
      evaluated > 0
        ? cleanBatchHistory.reduce(
            (sum, item) =>
              sum + Number(item.roi_percent || 0),
            0
          ) / evaluated
        : 0;

    return {
      outcomes_recorded: evaluated,
      correct_delay_predictions: correctPredictions,
      prediction_accuracy:
        evaluated > 0
          ? (correctPredictions / evaluated) * 100
          : 0,
      successful_decisions: successfulDecisions,
      decision_success_rate:
        evaluated > 0
          ? (successfulDecisions / evaluated) * 100
          : 0,
      on_time_shipments: onTimeShipments,
      delayed_shipments: delayedShipments,
      average_cost_variance_usd: averageCostVariance,
      total_estimated_savings_usd: totalSavings,
      average_roi_percent: averageRoi,
    };
  }, [cleanBatchHistory]);
  const performanceData = history.map((item) => ({
    name: `#${item.decision_id}`,
    predicted: Number(
      (item.predicted_delay_probability * 100).toFixed(2)
    ),
    actual: item.actual_delay_flag ? 100 : 0,
  }));

  const outcomeData = [
    {
      name: "On Time",
      value: summary?.on_time_shipments || 0,
    },
    {
      name: "Delayed",
      value: summary?.delayed_shipments || 0,
    },
  ];

  const evaluated = summary?.outcomes_recorded || 0;

  const onTimeRate = evaluated
    ? ((summary?.on_time_shipments || 0) / evaluated) * 100
    : 0;

  const renderPage = () => {
    switch (activePage) {
      case "Decisions":
        return (
          <DecisionsPage
            decisions={decisions}
            history={history}
          />
        );

      case "Outcomes":
        return (
          <OutcomesPage
            summary={summary}
            history={history}
            outcomeData={outcomeData}
          />
        );

      case "Analytics":
        return (
          <AnalyticsPage
            summary={cleanBatchSummary}
            history={cleanBatchHistory}
            actionData={cleanBatchActionData}
            performanceData={cleanBatchPerformanceData}
          />
        );

      case "Models":
        return (
          <ModelsPage
            models={models}
            activeModel={activeModel}
          />
        );

      case "System":
        return (
          <SystemPage
            health={health}
            loading={loading}
          />
        );

      default:
        return (
          <DashboardPage
            summary={summary}
            history={history}
            health={health}
            performanceData={performanceData}
            actionData={actionData}
            outcomeData={outcomeData}
            evaluated={evaluated}
            onTimeRate={onTimeRate}
          />
        );
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">
            <Truck size={21} />
          </div>

          <div>
            <strong>SUPPLY</strong>
            <span>PRESCRIPT</span>
          </div>
        </div>

        <div className="workspace">
          <span className="workspace-label">WORKSPACE</span>

          <div className="workspace-box">
            <div className="workspace-avatar">SP</div>

            <div>
              <strong>Supply Operations</strong>
              <span>Production</span>
            </div>

            <ChevronRight size={15} />
          </div>
        </div>

        <nav className="navigation">
          <span className="nav-label">MONITORING</span>

          <NavButton
            name="Dashboard"
            icon={<LayoutDashboard size={17} />}
            active={activePage}
            setActive={setActivePage}
          />

          <NavButton
            name="Decisions"
            icon={<Target size={17} />}
            active={activePage}
            setActive={setActivePage}
            count={summary?.total_decisions || 0}
          />

          <NavButton
            name="Outcomes"
            icon={<CheckCircle2 size={17} />}
            active={activePage}
            setActive={setActivePage}
            count={summary?.outcomes_recorded || 0}
          />

          <NavButton
            name="Analytics"
            icon={<BarChart3 size={17} />}
            active={activePage}
            setActive={setActivePage}
          />

          <NavButton
            name="Models"
            icon={<Database size={17} />}
            active={activePage}
            setActive={setActivePage}
          />

          <span className="nav-label system-label">SYSTEM</span>

          <NavButton
            name="System"
            icon={<Settings size={17} />}
            active={activePage}
            setActive={setActivePage}
          />
        </nav>

        <div className="sidebar-bottom">
          <div className="pipeline-status">
            <div className="pipeline-icon">
              <Zap size={15} />
            </div>

            <div>
              <strong>Pipeline Active</strong>
              <span>ML workflow online</span>
            </div>
          </div>

          <span className="live-dot" />
        </div>

        <div className="sidebar-footer">
          <span>Supply Prescript</span>
          <span>v{health?.version || "1.0.0"}</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Supply Operations</span>
            <ChevronRight size={14} />
            <strong>{activePage}</strong>
          </div>

          <div className="top-actions">
            <div className="connection-status">
              <span
                className={`connection-dot ${
                  health?.status === "healthy" ? "online" : ""
                }`}
              />

              <span>
                {health?.status === "healthy"
                  ? "Operational"
                  : "Offline"}
              </span>
            </div>

            <button
              className="refresh-btn"
              onClick={loadDashboard}
              disabled={loading}
            >
              <RefreshCw
                size={15}
                className={loading ? "spin" : ""}
              />
              Refresh
            </button>
          </div>
        </header>

        <div className="content">
          {error && (
            <div className="error-box">
              <AlertTriangle size={18} />

              <div>
                <strong>Dashboard connection error</strong>
                <span>{error}</span>
              </div>

              <button onClick={loadDashboard}>
                Retry
              </button>
            </div>
          )}

          {renderPage()}

          <footer className="dashboard-footer">
            <div>
              <span>API</span>
              <strong>
                {health?.service || "Supply Prescript API"}
              </strong>
            </div>

            <div>
              <span>VERSION</span>
              <strong>{health?.version || "1.0.0"}</strong>
            </div>

            <div>
              <span>ARCHITECTURE</span>
              <strong>
                ML → SHAP → Optimization → Execution → Outcomes
              </strong>
            </div>
          </footer>
        </div>
      </main>
    </div>
  );
}

function NavButton({
  name,
  icon,
  active,
  setActive,
  count,
}) {
  return (
    <button
      className={`nav-item ${
        active === name ? "active" : ""
      }`}
      onClick={() => setActive(name)}
    >
      {icon}
      <span>{name}</span>

      {count !== undefined && <small>{count}</small>}
    </button>
  );
}

function PageHeading({
  kicker,
  title,
  description,
  icon = <Activity size={14} />,
}) {
  return (
    <section className="page-heading">
      <div>
        <div className="heading-kicker">
          {icon}
          {kicker}
        </div>

        <h1>{title}</h1>
        <p>{description}</p>
      </div>
    </section>
  );
}

function DashboardPage({
  summary,
  history,
  health,
  performanceData,
  actionData,
  outcomeData,
  evaluated,
  onTimeRate,
}) {
  return (
    <>
      <PageHeading
        kicker="OPERATIONS CONTROL CENTER"
        title="Decision Intelligence"
        description="Monitor supply chain risk, operational decisions and real-world outcomes from a single closed-loop system."
      />

      <section className="kpi-grid">
        <MetricCard
          icon={<Activity />}
          label="Total Decisions"
          value={summary?.total_decisions || 0}
          description="Recorded decisions"
        />

        <MetricCard
          icon={<Zap />}
          label="Executed"
          value={summary?.executed_decisions || 0}
          description={`${evaluated} outcomes recorded`}
        />

        <MetricCard
          icon={<ShieldCheck />}
          label="Prediction Accuracy"
          value={formatPercent(summary?.prediction_accuracy)}
          description={`${summary?.correct_delay_predictions || 0} correct predictions`}
          positive
        />

        <MetricCard
          icon={<CheckCircle2 />}
          label="Decision Success"
          value={formatPercent(summary?.decision_success_rate)}
          description={`${summary?.successful_decisions || 0} successful decisions`}
          positive
        />

        <MetricCard
          icon={<CircleDollarSign />}
          label="Cost Variance"
          value={formatCurrency(
            summary?.average_cost_variance_usd
          )}
          description="Average evaluated variance"
        />

        <MetricCard
          icon={<BarChart3 />}
          label="On-Time Rate"
          value={formatPercent(onTimeRate)}
          description={`${summary?.on_time_shipments || 0} on-time outcomes`}
          positive
        />
      </section>

      <section className="charts-grid">
        <ChartPanel
          label="PREDICTION PERFORMANCE"
          title="Risk vs Actual Outcome"
        >
          <RiskChart data={performanceData} />
        </ChartPanel>

        <ChartPanel
          label="DECISION MIX"
          title="Selected Actions"
        >
          <ActionChart data={actionData} />
        </ChartPanel>
      </section>

      <section className="secondary-grid">
        <OutcomePanel
          summary={summary}
          outcomeData={outcomeData}
          evaluated={evaluated}
        />

        <SystemPanel health={health} />
      </section>

      <DecisionTable
        history={history}
        title="Recent Decisions"
        label="CLOSED-LOOP ACTIVITY"
      />
    </>
  );
}

function DecisionsPage({ decisions, history }) {
  const [filter, setFilter] = useState("ALL");

  const filtered =
    filter === "ALL"
      ? decisions
      : decisions.filter(
          (d) => d.decision_status === filter
        );

  return (
    <>
      <PageHeading
        kicker="DECISION CENTER"
        title="Operational Decisions"
        description="Review recommendations, selected actions and execution status for every shipment decision."
        icon={<Target size={14} />}
      />

      <section className="kpi-grid compact-kpis">
        <MetricCard
          icon={<Target />}
          label="All Decisions"
          value={decisions.length}
          description="Decision records"
        />

        <MetricCard
          icon={<Zap />}
          label="Executed"
          value={
            decisions.filter(
              (d) =>
                d.decision_status === "EXECUTED" ||
                d.decision_status === "OUTCOME_RECORDED"
            ).length
          }
          description="Executed workflows"
          positive
        />

        <MetricCard
          icon={<CheckCircle2 />}
          label="Evaluated"
          value={history.length}
          description="With actual outcomes"
          positive
        />

        <MetricCard
          icon={<Clock3 />}
          label="Pending"
          value={
            decisions.filter(
              (d) =>
                d.decision_status !== "EXECUTED" &&
                d.decision_status !== "OUTCOME_RECORDED"
            ).length
          }
          description="Need action"
        />
      </section>

      <section className="card decisions-card">
        <div className="page-toolbar">
          <div>
            <span className="card-label">
              DECISION REGISTER
            </span>
            <h2>All Decisions</h2>
          </div>

          <div className="filter-group">
            {[
              "ALL",
              "SELECTED",
              "EXECUTED",
              "OUTCOME_RECORDED",
            ].map((f) => (
              <button
                key={f}
                className={
                  filter === f ? "filter-active" : ""
                }
                onClick={() => setFilter(f)}
              >
                {f.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Shipment</th>
                <th>Recommended</th>
                <th>Selected</th>
                <th>Risk</th>
                <th>Estimated Cost</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {filtered.map((d) => (
                <tr key={d.id}>
                  <td>
                    <span className="decision-number">
                      #{d.id}
                    </span>
                  </td>

                  <td>Shipment #{d.shipment_id}</td>

                  <td>
                    <span className="action-pill">
                      {d.recommended_action}
                    </span>
                  </td>

                  <td>
                    <b>{d.selected_action}</b>
                  </td>

                  <td>
                    {(
                      Number(
                        d.predicted_delay_probability
                      ) * 100
                    ).toFixed(2)}
                    %
                  </td>

                  <td>
                    {formatCurrency(
                      d.estimated_cost_usd
                    )}
                  </td>

                  <td>
                    <span
                      className={`status-pill ${
                        d.decision_status ===
                          "OUTCOME_RECORDED" ||
                        d.decision_status === "EXECUTED"
                          ? "success"
                          : "warning"
                      }`}
                    >
                      {d.decision_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {!filtered.length && (
            <EmptyState text="No decisions match this filter" />
          )}
        </div>
      </section>
    </>
  );
}

function OutcomesPage({
  summary,
  history,
  outcomeData,
}) {
  return (
    <>
      <PageHeading
        kicker="OUTCOME MONITOR"
        title="Real-World Outcomes"
        description="Compare predictions and decisions against actual shipment performance to close the learning loop."
        icon={<CheckCircle2 size={14} />}
      />

      <section className="kpi-grid compact-kpis">
        <MetricCard
          icon={<CheckCircle2 />}
          label="On Time"
          value={summary?.on_time_shipments || 0}
          description="Successful shipment outcomes"
          positive
        />

        <MetricCard
          icon={<AlertTriangle />}
          label="Delayed"
          value={summary?.delayed_shipments || 0}
          description="Actual delayed shipments"
        />

        <MetricCard
          icon={<ShieldCheck />}
          label="Prediction Accuracy"
          value={formatPercent(
            summary?.prediction_accuracy
          )}
          description="Predicted vs actual"
          positive
        />

        <MetricCard
          icon={<CircleDollarSign />}
          label="Cost Variance"
          value={formatCurrency(
            summary?.average_cost_variance_usd
          )}
          description="Average difference"
        />
      </section>

      <section className="secondary-grid">
        <OutcomePanel
          summary={summary}
          outcomeData={outcomeData}
          evaluated={summary?.outcomes_recorded || 0}
        />

        <div className="card">
          <CardHeader
            label="EVALUATION RESULTS"
            title="Prediction Accuracy by Decision"
            icon={<BarChart3 size={18} />}
          />

          <div className="chart-area">
            <OutcomeAccuracyChart history={history} />
          </div>
        </div>
      </section>

      <DecisionTable
        history={history}
        title="Evaluated Outcomes"
        label="OUTCOME HISTORY"
      />
    </>
  );
}

function AnalyticsPage({
  summary,
  history,
  actionData,
  performanceData,
}) {
  return (
    <>
      <PageHeading
        kicker="ANALYTICS"
        title="Performance Analytics"
        description="Understand model performance, decision behavior, outcome quality and financial impact."
        icon={<BarChart3 size={14} />}
      />

      <section className="charts-grid">
        <ChartPanel
          label="MODEL PERFORMANCE"
          title="Prediction Risk Trend"
        >
          <RiskChart data={performanceData} />
        </ChartPanel>

        <ChartPanel
          label="ACTION ANALYSIS"
          title="Decision Distribution"
        >
          <ActionChart data={actionData} />
        </ChartPanel>
      </section>

      <section className="analytics-stat-grid">
        <AnalyticsStat
          label="Prediction Accuracy"
          value={formatPercent(
            summary?.prediction_accuracy
          )}
        />

        <AnalyticsStat
          label="Decision Success"
          value={formatPercent(
            summary?.decision_success_rate
          )}
        />

        <AnalyticsStat
          label="Average ROI"
          value={formatPercent(
            summary?.average_roi_percent
          )}
        />

        <AnalyticsStat
          label="Estimated Savings"
          value={formatCurrency(
            summary?.total_estimated_savings_usd
          )}
        />
      </section>

      <section className="card">
        <CardHeader
          label="DECISION QUALITY"
          title="Prediction vs Actual Detail"
          icon={<Activity size={18} />}
        />

        <div className="chart-area">
          <OutcomeAccuracyChart history={history} />
        </div>
      </section>
    </>
  );
}

function ModelsPage({ models, activeModel }) {
  return (
    <>
      <PageHeading
        kicker="MLOPS / MODEL REGISTRY"
        title="Model Management"
        description="Track active and archived prediction models, their evaluation metrics and production status."
        icon={<Database size={14} />}
      />

      {activeModel && (
        <section className="card active-model-card">
          <CardHeader
            label="ACTIVE PRODUCTION MODEL"
            title={activeModel.version}
            icon={<ShieldCheck size={18} />}
            right={
              <span className="status-pill success">
                {activeModel.status}
              </span>
            }
          />

          <div className="model-overview">
            <div className="model-main">
              <span className="model-type">
                {activeModel.model_type}
              </span>

              <h3>{activeModel.model_name}</h3>

              <p>
                {activeModel.description ||
                  "Active production model used by the prediction engine."}
              </p>

              <div className="model-path">
                <span>MODEL PATH</span>
                <code>{activeModel.model_path}</code>
              </div>
            </div>

            <div className="model-metrics">
              <ModelMetric
                label="Accuracy"
                value={formatPercent(
                  activeModel.accuracy * 100
                )}
              />

              <ModelMetric
                label="Precision"
                value={formatPercent(
                  activeModel.precision * 100
                )}
              />

              <ModelMetric
                label="Recall"
                value={formatPercent(
                  activeModel.recall * 100
                )}
              />

              <ModelMetric
                label="F1 Score"
                value={formatPercent(
                  activeModel.f1_score * 100
                )}
              />

              <ModelMetric
                label="ROC-AUC"
                value={formatPercent(
                  activeModel.roc_auc * 100
                )}
              />

              <ModelMetric
                label="Features"
                value={activeModel.feature_count}
              />
            </div>
          </div>
        </section>
      )}

      <section className="card model-registry-card">
        <CardHeader
          label="MODEL REGISTRY"
          title="Registered Models"
          icon={<Database size={18} />}
          right={
            <span className="record-pill">
              {models.length} models
            </span>
          }
        />

        <div className="table-container">
          <table className="model-registry-table">
            <thead>
              <tr>
                <th className="model-index-col">#</th>
                <th>Model Version</th>
                <th>Model Type</th>
                <th>Status</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1</th>
                <th>ROC-AUC</th>
              </tr>
            </thead>

            <tbody>
              {models.map((model, index) => (
                <tr key={model.id}>
                  <td className="model-index-col">
                    <span className="model-index">
                      {index + 1}
                    </span>
                  </td>

                  <td>
                    <span className="model-version">
                      {model.version}
                    </span>
                  </td>

                  <td>
                    <span className="model-type-cell">
                      {model.model_type}
                    </span>
                  </td>

                  <td>
                    {model.status === "ACTIVE" ? (
                      <span className="model-status-active">
                        <i />
                        ACTIVE
                      </span>
                    ) : (
                      <span className="status-pill archived">
                        {model.status}
                      </span>
                    )}
                  </td>

                  <td>
                    <span className="model-metric-value">
                      {formatPercent(
                        model.accuracy * 100
                      )}
                    </span>
                  </td>

                  <td>
                    <span className="model-metric-value">
                      {formatPercent(
                        model.precision * 100
                      )}
                    </span>
                  </td>

                  <td>
                    <span className="model-metric-value">
                      {formatPercent(
                        model.recall * 100
                      )}
                    </span>
                  </td>

                  <td>
                    <span className="model-metric-value">
                      {formatPercent(
                        model.f1_score * 100
                      )}
                    </span>
                  </td>

                  <td>
                    <span className="model-metric-value">
                      {formatPercent(
                        model.roc_auc * 100
                      )}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {!models.length && (
            <EmptyState text="No registered models available" />
          )}
        </div>
      </section>
    </>
  );
}

function ModelMetric({ label, value }) {
  return (
    <div className="model-metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function SystemPage({ health, loading }) {
  return (
    <>
      <PageHeading
        kicker="SYSTEM"
        title="Platform Health"
        description="Monitor the health of the Supply Prescript intelligence pipeline and connected services."
        icon={<Settings size={14} />}
      />

      <section className="system-overview">
        <div className="system-hero">
          <div className="system-health-icon">
            <CheckCircle2 size={28} />
          </div>

          <div>
            <span>PLATFORM STATUS</span>

            <h2>
              {health?.status === "healthy"
                ? "All systems operational"
                : "System unavailable"}
            </h2>

            <p>
              {health?.service || "Supply Prescript API"} ·
              Version {health?.version || "1.0.0"}
            </p>
          </div>
        </div>
      </section>

      <section className="system-grid">
        <SystemPanel health={health} />

        <div className="card">
          <CardHeader
            label="ARCHITECTURE"
            title="Closed-Loop Pipeline"
            icon={<Activity size={18} />}
          />

          <div className="architecture-list">
            <ArchStep
              n="01"
              title="Prediction"
              text="XGBoost delay-risk model"
            />

            <ArchStep
              n="02"
              title="Explainability"
              text="SHAP feature attribution"
            />

            <ArchStep
              n="03"
              title="Optimization"
              text="Prescriptive action policy"
            />

            <ArchStep
              n="04"
              title="Evaluation"
              text="Actual outcome feedback"
            />
          </div>
        </div>
      </section>

      {loading && (
        <div className="loading-note">
          <RefreshCw size={14} className="spin" />
          Refreshing system status...
        </div>
      )}
    </>
  );
}

function ChartPanel({
  label,
  title,
  children,
}) {
  return (
    <div className="card">
      <CardHeader
        label={label}
        title={title}
        icon={<Activity size={18} />}
      />

      {children}
    </div>
  );
}

function RiskChart({ data }) {
  const maxPredicted = Math.max(
    ...data.map((item) => Number(item.predicted || 0)),
    0
  );

  const yMax =
    maxPredicted <= 10
      ? 10
      : maxPredicted <= 25
      ? 25
      : maxPredicted <= 50
      ? 50
      : 100;

  return (
    <>
      <div className="chart-area">
        {data.length ? (
          <ResponsiveContainer width="100%" height={270}>
            <AreaChart data={data}>
              <defs>
                <linearGradient
                  id="riskGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor="#6366f1"
                    stopOpacity={0.25}
                  />

                  <stop
                    offset="100%"
                    stopColor="#6366f1"
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>

              <CartesianGrid
                stroke="#eef0f4"
                vertical={false}
              />

              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />

              <YAxis
                domain={[0, yMax]}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
                tickFormatter={(value) => `${value}%`}
              />

              <Tooltip
                formatter={(value, name) => [
                  `${Number(value).toFixed(2)}%`,
                  name,
                ]}
              />

              <Area
                type="monotone"
                dataKey="predicted"
                stroke="#6366f1"
                strokeWidth={2.5}
                fill="url(#riskGradient)"
                name="Predicted Risk"
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <EmptyState text="No evaluation data available" />
        )}
      </div>

      <div className="chart-footer">
        <div>
          <span className="legend-indicator indigo" />
          Predicted risk
        </div>
      </div>
    </>
  );
}

function ActionChart({ data }) {
  return (
    <div className="chart-area">
      {data.length ? (
        <ResponsiveContainer
          width="100%"
          height={270}
        >
          <BarChart data={data}>
            <CartesianGrid
              stroke="#eef0f4"
              vertical={false}
            />

            <XAxis
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10 }}
            />

            <YAxis
              allowDecimals={false}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11 }}
            />

            <Tooltip />

            <Bar
              dataKey="value"
              fill="#6366f1"
              radius={[7, 7, 0, 0]}
              barSize={42}
            />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <EmptyState text="No decision data available" />
      )}
    </div>
  );
}

function OutcomeAccuracyChart({ history }) {
  const data = history.map((item) => ({
    name: `#${item.decision_id}`,
    predicted: Number(
      (Number(item.predicted_delay_probability) * 100).toFixed(2)
    ),
    actual: item.actual_delay_flag === 1 ? 1 : 0,
    actualLabel:
      item.actual_delay_flag === 1 ? "DELAYED" : "ON_TIME",
  }));

  return (
    <div className="chart-area">
      {data.length ? (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid
              stroke="#eef0f4"
              vertical={false}
            />

            <XAxis
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11 }}
            />

            <YAxis
              domain={[0, 100]}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11 }}
              tickFormatter={(value) => `${value}%`}
            />

            <Tooltip
              formatter={(value, name) => {
                if (name === "Predicted Risk") {
                  return [
                    `${Number(value).toFixed(2)}%`,
                    name,
                  ];
                }

                return [
                  value === 1 ? "DELAYED" : "ON TIME",
                  "Actual Outcome",
                ];
              }}
            />

            <Bar
              dataKey="predicted"
              fill="#6366f1"
              radius={[6, 6, 0, 0]}
              name="Predicted Risk"
            />

            <Bar
              dataKey="actual"
              fill="#22c55e"
              radius={[6, 6, 0, 0]}
              name="Actual Outcome"
            />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <EmptyState text="No evaluation data available" />
      )}
    </div>
  );
}
function OutcomePanel({
  summary,
  outcomeData,
  evaluated,
}) {
  return (
    <div className="card">
      <CardHeader
        label="OUTCOME MONITOR"
        title="Shipment Outcomes"
        icon={<CheckCircle2 size={18} />}
      />

      <div className="outcome-body">
        <div className="donut">
          <ResponsiveContainer
            width="100%"
            height={190}
          >
            <PieChart>
              <Pie
                data={outcomeData}
                dataKey="value"
                nameKey="name"
                innerRadius={55}
                outerRadius={76}
                paddingAngle={5}
              >
                <Cell fill="#22c55e" />
                <Cell fill="#ef4444" />
              </Pie>

              <Tooltip />
            </PieChart>

            <div className="donut-center">
              <strong>{evaluated}</strong>
              <span>evaluated</span>
            </div>
          </ResponsiveContainer>
        </div>

        <div className="outcome-stats">
          <OutcomeStat
            color="green"
            label="On Time"
            value={summary?.on_time_shipments || 0}
          />

          <OutcomeStat
            color="red"
            label="Delayed"
            value={summary?.delayed_shipments || 0}
          />
        </div>
      </div>
    </div>
  );
}
function SystemPanel({ health }) {
  return (
    <div className="card">
      <CardHeader
        label="SYSTEM STATUS"
        title="Pipeline Health"
        icon={<Activity size={18} />}
      />

      <div className="health-list">
        <HealthRow
          label="API Service"
          value={
            health?.service || "Supply Prescript API"
          }
          status={health?.status === "healthy"}
        />

        <HealthRow
          label="Prediction Engine"
          value="XGBoost"
          status
        />

        <HealthRow
          label="Explainability"
          value="SHAP"
          status
        />

        <HealthRow
          label="Optimization"
          value="Prescriptive Policy"
          status
        />

        <HealthRow
          label="Evaluation Loop"
          value="Active"
          status
        />
      </div>
    </div>
  );
}

function DecisionTable({
  history,
  title,
  label,
}) {
  return (
    <section className="card decisions-card">
      <CardHeader
        label={label}
        title={title}
        icon={<Clock3 size={18} />}
        right={
          <span className="record-pill">
            {history.length} records
          </span>
        }
      />

      {history.length ? (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Decision</th>
                <th>Shipment</th>
                <th>Action</th>
                <th>Predicted Risk</th>
                <th>Outcome</th>
                <th>Cost Variance</th>
                <th>Result</th>
              </tr>
            </thead>

            <tbody>
              {history.map((item) => (
                <tr key={item.decision_id}>
                  <td>
                    <span className="decision-number">
                      #{item.decision_id}
                    </span>
                  </td>

                  <td>
                    <span className="shipment-name">
                      Shipment #{item.shipment_id}
                    </span>
                  </td>

                  <td>
                    <span className="action-pill">
                      {item.selected_action}
                    </span>
                  </td>

                  <td>
                    <div className="risk-value">
                      <div className="mini-risk">
                        <div
                          style={{
                            width: `${Math.min(
                              item.predicted_delay_probability *
                                100,
                              100
                            )}%`,
                          }}
                        />
                      </div>

                      <span>
                        {(
                          item.predicted_delay_probability *
                          100
                        ).toFixed(2)}
                        %
                      </span>
                    </div>
                  </td>

                  <td>
                    <span
                      className={`status-pill ${
                        item.outcome_status === "ON_TIME"
                          ? "success"
                          : "danger"
                      }`}
                    >
                      {item.outcome_status}
                    </span>
                  </td>

                  <td>
                    <span
                      className={
                        item.cost_variance_usd > 0
                          ? "cost-negative"
                          : "cost-positive"
                      }
                    >
                      {formatCurrency(
                        item.cost_variance_usd
                      )}
                    </span>
                  </td>

                  <td>
                    {item.decision_success ? (
                      <span className="result-success">
                        <CheckCircle2 size={15} />
                        Successful
                      </span>
                    ) : (
                      <span className="result-danger">
                        <AlertTriangle size={15} />
                        Review
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState text="No records available" />
      )}
    </section>
  );
}

function AnalyticsStat({ label, value }) {
  return (
    <div className="analytics-stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ArchStep({ n, title, text }) {
  return (
    <div className="arch-step">
      <b>{n}</b>

      <div>
        <strong>{title}</strong>
        <span>{text}</span>
      </div>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  description,
  positive = false,
}) {
  return (
    <div className="metric-card">
      <div
        className={`metric-icon ${
          positive ? "positive" : ""
        }`}
      >
        {icon}
      </div>

      <div className="metric-info">
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{description}</small>
      </div>
    </div>
  );
}

function CardHeader({
  label,
  title,
  icon,
  right,
}) {
  return (
    <div className="card-header">
      <div>
        <span className="card-label">{label}</span>
        <h2>{title}</h2>
      </div>

      <div className="header-right">
        {right}
        {icon}
      </div>
    </div>
  );
}

function HealthRow({
  label,
  value,
  status,
}) {
  return (
    <div className="health-row">
      <div>
        <strong>{label}</strong>
        <span>{value}</span>
      </div>

      <span
        className={`health-status ${
          status ? "active" : ""
        }`}
      >
        <i />
        {status ? "Healthy" : "Offline"}
      </span>
    </div>
  );
}

function OutcomeStat({
  color,
  label,
  value,
}) {
  return (
    <div className="outcome-stat">
      <span
        className={`outcome-dot ${color}`}
      />

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function EmptyState({ text }) {
  return (
    <div className="empty-state">
      <Activity size={25} />
      <span>{text}</span>
    </div>
  );
}

export default App;
