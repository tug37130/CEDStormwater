/** @jsx jsx */
import { React, jsx, AllWidgetProps } from 'jimu-core';
import { Chart, Bar } from 'react-chartjs-2';
import 'chart.js/auto';
import scenarioData from '../data/scenario.json';

export default class TableWidget extends React.PureComponent<AllWidgetProps<unknown>, { scenario: any }> {
  constructor(props) {
    super(props);
    this.state = {
      scenario: scenarioData
    };
  }

  componentDidMount() {
    window.addEventListener("scenario-changed", this.handleScenarioChanged);
  }

  componentWillUnmount() {
    window.removeEventListener("scenario-changed", this.handleScenarioChanged);
  }

  handleScenarioChanged = (evt: any) => {
    const newScenario = evt.detail.scenario;
    if (!newScenario) return;
    console.log("TableWidget => new scenario arrived, updating table.");
    this.setState({ scenario: newScenario });
  };

  getCostPerYear = () => {
    const costByYear: { [year: number]: number } = {};
    const { scenario } = this.state;
    scenario.Treatments.forEach((t) => {
      const year = t.Year || 0;
      const totalCost =
        (t.Cost || t.DirectCost || 0) +
        (t.DesignCost || 0) +
        (t.ROWCost || 0) +
        (t.UtilCost || 0) +
        (t.OtherCost || 0);
      costByYear[year] = (costByYear[year] || 0) + totalCost;
    });
    return costByYear;
  };

  getTreatmentTypeCounts = () => {
    const treatmentCounts: { [type: string]: number } = {};
    const { scenario } = this.state;
    scenario.Treatments.forEach((t) => {
      const type = t.TreatType || t.TreatmentType || 'Unknown';
      treatmentCounts[type] = (treatmentCounts[type] || 0) + 1;
    });
    return treatmentCounts;
  };

  render() {
    const costData = this.getCostPerYear();
    const costChartData = {
      labels: Object.keys(costData),
      datasets: [
        {
          label: 'Total Cost ($)',
          data: Object.values(costData),
          backgroundColor: 'rgba(21, 52, 106, 0.6)',
          borderColor: 'rgba(11, 8, 53, 1)',
          borderWidth: 1
        }
      ]
    };

    const treatmentData = this.getTreatmentTypeCounts();
    const treatmentChartData = {
      labels: Object.keys(treatmentData),
      datasets: [
        {
          label: 'Number of Treatments',
          data: Object.values(treatmentData),
          backgroundColor: 'rgba(0, 137, 69, 0.6)',
          borderColor: 'rgba(0, 60, 30, 1)',
          borderWidth: 1
        }
      ]
    };

    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          padding: '20px',
          height: '400px',
          overflow: 'hidden'
        }}
      >
        <div style={{ width: '48%', height: '100%', display: 'flex', flexDirection: 'column' }}>
          <h3>Total Cost Per Year</h3>
          <Bar data={costChartData} options={{ responsive: true, maintainAspectRatio: true }} />
        </div>
        <div style={{ width: '48%', height: '100%', display: 'flex', flexDirection: 'column' }}>
          <h3>Treatment Breakdown</h3>
          <Bar data={treatmentChartData} options={{ responsive: true, maintainAspectRatio: true }} />
        </div>
      </div>
    );
  }
}
