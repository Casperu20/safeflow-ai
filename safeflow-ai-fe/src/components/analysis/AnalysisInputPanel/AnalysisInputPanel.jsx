import "./AnalysisInputPanel.css";
import trashIcon from "../../../assets/images/Trash2.png";
import sendIcon from "../../../assets/images/Send.png";

export function AnalysisInputPanel({ value, isSubmitting, onChange, onClear, onSubmit }) {
  return (
    <div className="analysis-input-panel">
      <textarea
        className="analysis-input-panel__textarea"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Paste your desired message to check for possible scams"
      />
      <div className="analysis-input-panel__actions">
        <button type="button" onClick={onClear}>
          <img src={trashIcon} alt="Trash icon" className="analysis-input-panel__icon" />
        </button>
        <button type="button" onClick={onSubmit} disabled={isSubmitting}>
          <img src={sendIcon} alt="Send icon" className="analysis-input-panel__icon" />
        </button>
      </div>
    </div>
  );
}
