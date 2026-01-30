import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Stage2.css';

export default function Stage2({ critiques }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!critiques || critiques.length === 0) {
    return null;
  }

  return (
    <div className="stage stage2">
      <h3 className="stage-title">Stage 2: Cross-Debate</h3>

      <p className="stage-description">
        Each philosopher read the others' answers and launched a direct critique—attacking by name, in character.
      </p>

      <div className="tabs">
        {critiques.map((item, index) => (
          <button
            key={index}
            className={`tab ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
          >
            {item.philosophier || item.model || '—'}
          </button>
        ))}
      </div>

      <div className="tab-content">
        <div className="ranking-model">
          {critiques[activeTab].philosophier || critiques[activeTab].model}
        </div>
        <div className="ranking-content markdown-content">
          <ReactMarkdown>{critiques[activeTab].critique || critiques[activeTab].ranking || ''}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
