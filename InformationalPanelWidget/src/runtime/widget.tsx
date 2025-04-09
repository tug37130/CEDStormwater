/** @jsx jsx */
import { React, AllWidgetProps, jsx } from 'jimu-core';
import scenarioData from '../data/scenario.json';
import eventEmitter from '../../../PennRoadSegments/src/singleton/EventEmitterInstance';

// Utility for formatting numbers (rounded to nearest dollar)
function formatNumber(value: number, isCurrency?: boolean) {
  if (value == null || isNaN(value)) return '';
  return new Intl.NumberFormat('en-US', {
    style: isCurrency ? 'currency' : 'decimal',
    currency: 'USD',
    minimumFractionDigits: isCurrency ? 0 : 0, // No decimal places
    maximumFractionDigits: isCurrency ? 0 : 0
  }).format(value);
}

// Helper function to map asset type codes to spelled-out labels
function getAssetTypeLabel(type: string) {
  if (type === 'P') return 'Pavement';
  if (type === 'C') return 'Combined';
  if (type === 'B') return 'Bridge';
  return type; // Fallback: if not one of the above, return the original value
}

// Example dictionary for county codes -> county names.
// (Adjust as needed with your full codes.)
const countyCodes: { [key: string]: string } = {
  '01': 'Adams',
  '02': 'Allegheny',
  '03': 'Armstrong',
  '04': 'Beaver',
  '05': 'Bedford',
  '06': 'Berks',
  '07': 'Blair',
  '08': 'Bradford',
  '09': 'Bucks',
  '10': 'Butler',
  '11': 'Cambria',
  '12': 'Cameron',
  '13': 'Carbon',
  '14': 'Centre',
  '15': 'Chester',
  '16': 'Clarion',
  '17': 'Clearfield',
  '18': 'Clinton',
  '19': 'Columbia',
  '20': 'Crawford',
  '21': 'Cumberland',
  '22': 'Dauphin',
  '23': 'Delaware',
  '24': 'Elk',
  '25': 'Erie',
  '26': 'Fayette',
  '27': 'Forest',
  '28': 'Franklin',
  '29': 'Fulton',
  '30': 'Greene',
  '31': 'Huntingdon',
  '32': 'Indiana',
  '33': 'Jefferson',
  '34': 'Juniata',
  '35': 'Lackawanna',
  '36': 'Lancaster',
  '37': 'Lawrence',
  '38': 'Lebanon',
  '39': 'Lehigh',
  '40': 'Luzerne',
  '41': 'Lycoming',
  '42': 'McKean',
  '43': 'Mercer',
  '44': 'Mifflin',
  '45': 'Monroe',
  '46': 'Montgomery',
  '47': 'Montour',
  '48': 'Northampton',
  '49': 'Northumberland',
  '50': 'Perry',
  '51': 'Philadelphia',
  '52': 'Pike',
  '53': 'Potter',
  '54': 'Schuylkill',
  '55': 'Snyder',
  '56': 'Somerset',
  '57': 'Sullivan',
  '58': 'Susquehanna',
  '59': 'Tioga',
  '60': 'Union',
  '61': 'Venango',
  '62': 'Warren',
  '63': 'Washington',
  '64': 'Wayne',
  '65': 'Westmoreland',
  '66': 'Wyoming',
  '67': 'York',
  '68': 'Out-of-State'
};

// Helper to get the county name from the numeric code
function getCountyName(code: number | null | undefined) {
  if (code == null) return '';
  // Convert the numeric code (e.g. 8) to a 2-digit string (e.g. "08") for lookup
  const padded = code.toString().padStart(2, '0');
  return countyCodes[padded] || ''; // fallback to '' if not found
}

// Helper function to sum all cost fields (direct + indirect) and round to nearest dollar
function calcTotalCost(treatment: any, edits: any) {
  const numericVal = (fieldName: string, fallback: number) => {
    const raw = edits[fieldName] ?? treatment[fieldName] ?? fallback;
    return typeof raw === 'number' ? raw : parseFloat(raw) || 0;
  };
  const direct = numericVal('Cost', 0);
  const design = numericVal('IndirectCostDesign', 0);
  const row = numericVal('IndirectCostROW', 0);
  const util = numericVal('IndirectCostUtilities', 0);
  const other = numericVal('IndirectCostOther', 0);
  return direct + design + row + util + other;
}

interface State {
  scenario: any;
  filteredProjects: any[];
  editedData: { [key: string]: any };
  searchValue: string;
  overrideProjects: any[] | null;
  selectedProject?: any;
  filteredTreatIds?: string[];
}

export default class InformationalPanelWidget extends React.PureComponent<
  AllWidgetProps<unknown>,
  State
> {
  constructor(props: AllWidgetProps<unknown>) {
    super(props);
    this.state = {
      scenario: scenarioData,
      filteredProjects: scenarioData?.Projects || [],
      editedData: {},
      searchValue: '',
      overrideProjects: null,
      selectedProject: null
    };
  }

  onScenarioChanged = (evt: any) => {
    const newScenario = evt.detail.scenario;
    if (!newScenario || !newScenario.Projects) {
      console.error('Invalid scenario received', newScenario);
      return;
    }
    console.log('Info Panel => New scenario arrived', newScenario);
    this.setState({
      scenario: newScenario,
      filteredProjects: newScenario.Projects,
      overrideProjects: null,
      editedData: {},
      selectedProject: null
    });
  };

  componentDidMount() {
    window.addEventListener('scenario-changed', this.onScenarioChanged);
    window.addEventListener('segment-selected', this.handleSegmentSelected);
    window.addEventListener('filter-updated', this.handleFilterUpdated);

    if (!this.state.scenario || !this.state.scenario.Projects) {
      this.setState({
        scenario: scenarioData,
        filteredProjects: scenarioData?.Projects || []
      });
    }
  }

  componentWillUnmount() {
    window.removeEventListener('scenario-changed', this.onScenarioChanged);
    window.removeEventListener('segment-selected', this.handleSegmentSelected);
    window.removeEventListener('filter-updated', this.handleFilterUpdated);
  }

  handleFilterUpdated = (evt: any) => {
    const { filteredProjIds, filteredTreatIds } = evt.detail;
    console.log('Info Panel => filter-updated event:', filteredProjIds, filteredTreatIds);

    const newProjects = this.state.scenario.Projects.filter((p: any) => {
      const pid = p.ProjId ?? p.ProjectID;
      return filteredProjIds.includes(pid);
    });

    this.setState({
      overrideProjects: newProjects,
      filteredTreatIds
    });
  };

  handleSegmentSelected = (event: CustomEvent) => {
    const projId = event.detail.projId;
    if (!this.state.scenario || !this.state.scenario.Projects) {
      console.error('Info Panel: No scenario data loaded, waiting for scenario...');
      return;
    }
    const selectedProject = this.state.scenario.Projects.find(
      (p: any) => (p.ProjId || p.ProjectID) === projId
    );
    if (!selectedProject) {
      console.warn('Info Panel: No matching project found for projId:', projId);
      return;
    }
    this.setState({ selectedProject });
  };

  handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const searchValue = e.target.value.toLowerCase();
    if (this.state.overrideProjects) {
      const filtered = this.state.overrideProjects.filter((p: any) =>
        String(p.ProjId || p.ProjectID).includes(searchValue)
      );
      this.setState({ searchValue, overrideProjects: filtered });
    } else {
      const filtered = this.state.filteredProjects.filter((p: any) =>
        String(p.ProjId || p.ProjectID).includes(searchValue)
      );
      this.setState({ searchValue, filteredProjects: filtered });
    }
  };

  handleProjectInputChange = (projectId: number, field: string, value: any) => {
    this.setState((prev) => ({
      editedData: {
        ...prev.editedData,
        [projectId]: {
          ...prev.editedData[projectId],
          [field]: value
        }
      }
    }));
  };

  handleTreatmentInputChange = (
    treatmentId: number | string,
    field: string,
    value: any
  ) => {
    this.setState((prev) => ({
      editedData: {
        ...prev.editedData,
        [`treatment-${treatmentId}`]: {
          ...prev.editedData[`treatment-${treatmentId}`],
          [field]: value
        }
      }
    }));
  };

  getUpdatedProjects() {
    return this.state.scenario.Projects.filter((p: any) => {
      const key = p.ProjId || p.ProjectID;
      return this.state.editedData.hasOwnProperty(key);
    }).map((p: any) => {
      const key = p.ProjId || p.ProjectID;
      const edits = this.state.editedData[key] || {};
      return { ...p, ...edits };
    });
  }

  getUpdatedTreatments() {
    return this.state.scenario.Treatments.filter((t: any) => {
      const key = `treatment-${t.TreatmentId || t.TreatmentID}`;
      return this.state.editedData.hasOwnProperty(key);
    }).map((t: any) => {
      const key = `treatment-${t.TreatmentId || t.TreatmentID}`;
      const edits = this.state.editedData[key] || {};
      return { ...t, ...edits };
    });
  }

  submitScenario = async () => {
    try {
      const scenarioMeta = this.state.scenario.Scenario || {};
      const updatedPayload = {
        Scenario: scenarioMeta,
        Projects: this.getUpdatedProjects(),
        Treatments: this.getUpdatedTreatments()
      };

      console.log('Minimal Scenario Payload:', JSON.stringify(updatedPayload, null, 2));

      const resp = await fetch('https://demo.pbweb.info/api/RunScenario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedPayload)
      });

      if (!resp.ok) {
        console.error('Submit failed');
        console.error(await resp.text());
      } else {
        console.log('Submit successful');
        const submittedEvent = new CustomEvent('scenario-submitted', {
          detail: { scenario: updatedPayload }
        });
        window.dispatchEvent(submittedEvent);
      }
    } catch (err) {
      console.error('Error submitting scenario:', err);
    }
  };

  render() {
    const {
      editedData,
      searchValue,
      overrideProjects,
      filteredProjects,
      selectedProject,
      filteredTreatIds
    } = this.state;

    // Decide which projects to show
    const finalProjectsToShow = selectedProject
      ? [selectedProject]
      : overrideProjects ?? filteredProjects;

    // For currency with no decimals
    const parseCurrencyInput = (input: string): number => {
      const raw = input.replace(/[^0-9.-]/g, '');
      const val = parseFloat(raw);
      return isNaN(val) ? NaN : val;
    };

    const formatCurrencyNoDecimals = (num: number) => {
      return formatNumber(num, true);
    };

    return (
      <div
        style={{
          width: '100%',
          height: '100%',
          padding: '10px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Search input if no project selected */}
        {!selectedProject && (
          <input
            type="text"
            placeholder="Search by Project ID..."
            value={searchValue}
            onChange={this.handleSearchChange}
            style={{
              width: '100%',
              padding: '10px',
              marginBottom: '10px',
              border: '1px solid #ccc',
              borderRadius: '5px'
            }}
          />
        )}

        {/* Clear selection if a project is selected */}
        {selectedProject && (
          <button
            onClick={() => this.setState({ selectedProject: null })}
            style={{ padding: '10px', marginBottom: '10px' }}
          >
            Clear Selection
          </button>
        )}

        <div style={{ flex: 1, overflowY: 'auto' }}>
          {finalProjectsToShow.map((project: any) => {
            const projectId = project.ProjId || project.ProjectID;
            const projectTreatments = this.state.scenario.Treatments.filter(
              (t: any) => (t.ProjId || t.ProjectID) === projectId
            );
            const displayedTreatments = filteredTreatIds
              ? projectTreatments.filter((t: any) => {
                  const tid = t.TreatId ?? t.TreatmentId ?? t.TreatmentID;
                  return filteredTreatIds.includes(tid);
                })
              : projectTreatments;

            const projEdits = editedData[projectId] || {};
            const yearVal = projEdits.Year ?? project.Year ?? '';

            return (
              <div
                key={projectId}
                style={{
                  border: '1px solid #000',
                  padding: '15px',
                  marginBottom: '20px',
                  borderRadius: '5px',
                  backgroundColor: '#fff'
                }}
              >
                {/* Project ID & Description, side by side */}
                <div style={{ display: 'flex', marginBottom: '20px' }}>
                  {/* "Project Identification" column */}
                  <div style={{ width: '200px', marginRight: '10px' }}>
                    <h4 style={{ marginTop: 0 }}>Project Identification</h4>
                    <div style={{ marginBottom: '8px' }}>
                      <label style={{ fontWeight: 'bold', display: 'block' }}>
                        Schema ID
                      </label>
                      <input
                        type="text"
                        readOnly
                        style={styles.readOnlyInput}
                        value={project.SchemaId || project.SystemID || ''}
                      />
                    </div>
                    <div style={{ marginBottom: '8px' }}>
                      <label style={{ fontWeight: 'bold', display: 'block' }}>
                        District
                      </label>
                      <input
                        type="number"
                        readOnly
                        style={styles.readOnlyInput}
                        value={displayedTreatments[0]?.Dist ?? ''}
                      />
                    </div>
                    {/* County numeric code stored in displayedTreatments[0]?.Cnty;
                        we do not display that numeric code directly. */}
                    <div style={{ marginBottom: '8px' }}>
                      <label style={{ fontWeight: 'bold', display: 'block' }}>
                        County
                      </label>
                      <input
                        type="text"
                        readOnly
                        style={styles.readOnlyInput}
                        value={
                          // Convert numeric code to county name
                          getCountyName(displayedTreatments[0]?.Cnty)
                        }
                      />
                    </div>
                    <div style={{ marginBottom: '8px' }}>
                      <label style={{ fontWeight: 'bold', display: 'block' }}>
                        Route
                      </label>
                      <input
                        type="number"
                        readOnly
                        style={styles.readOnlyInput}
                        value={displayedTreatments[0]?.Rte ?? ''}
                      />
                    </div>
                  </div>

                  {/* "Project Description" column */}
                  <div style={{ width: '200px', marginRight: '10px' }}>
                    <h4 style={{ marginTop: 0 }}>Project Description</h4>
                    <div style={{ marginBottom: '8px' }}>
                      <label style={{ fontWeight: 'bold', display: 'block' }}>
                        User ID
                      </label>
                      <input
                        type="number"
                        style={styles.editableInput}
                        value={projEdits.UserID ?? project.UserID ?? ''}
                        onChange={(e) =>
                          this.handleProjectInputChange(projectId, 'UserID', e.target.value)
                        }
                      />
                    </div>
                    <div style={{ marginBottom: '8px' }}>
                      <label style={{ fontWeight: 'bold', display: 'block' }}>
                        Year
                      </label>
                      <input
                        type="number"
                        style={styles.editableInput}
                        value={yearVal}
                        onChange={(e) =>
                          this.handleProjectInputChange(projectId, 'Year', e.target.value)
                        }
                      />
                    </div>
                  </div>

                  {/* Notes column expands to fill space */}
                  <div style={{ flex: 1, marginLeft: '10px' }}>
                    <h4 style={{ marginTop: 0 }}>Notes</h4>
                    <textarea
                      rows={6}
                      style={{ width: '100%', textAlign: 'left' }}
                      placeholder="Enter notes here..."
                      value={projEdits.Notes ?? project.Notes ?? ''}
                      onChange={(e) =>
                        this.handleProjectInputChange(projectId, 'Notes', e.target.value)
                      }
                    />
                  </div>
                </div>

                {/* Treatments Table */}
                <h4>Treatments</h4>
                <table
                  style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    marginBottom: '20px'
                  }}
                >
                  <thead>
                    <tr style={styles.headerRow}>
                      <th style={styles.cell}>Committed</th>
                      {/* Proj ID */}
                      <th style={styles.smallerCell}>Proj ID</th>
                      {/* Asset */}
                      <th style={styles.mediumCell}>Asset</th>
                      {/* County (NEW COLUMN) */}
                      <th style={styles.mediumCell}>County</th>
                      {/* Route */}
                      <th style={styles.smallerCell}>Route</th>
                      {/* Section */}
                      <th style={styles.mediumCell}>Section</th>
                      {/* Rename Bridge ID => BRKEY */}
                      <th style={styles.mediumCell}>BRKEY</th>
                      {/* MPMS ID */}
                      <th style={styles.smallerCell}>MPMS ID</th>
                      {/* Treat Type */}
                      <th style={styles.cell}>Treat Type</th>
                      {/* Treatment */}
                      <th style={styles.cell}>Treatment</th>
                      {/* PreferredYear */}
                      <th style={styles.smallCell}>Pref Year</th>
                      {/* MinYear */}
                      <th style={styles.smallCell}>Min Year</th>
                      {/* MaxYear */}
                      <th style={styles.smallCell}>Max Year</th>
                      {/* Benefit */}
                      <th style={styles.cell}>Benefit</th>
                      {/* Total Cost */}
                      <th style={styles.cell}>Total Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {displayedTreatments.map((t: any) => {
                      const tKey = `treatment-${t.TreatmentId || t.TreatmentID}`;
                      const tEdits = editedData[tKey] || {};

                      // Is it committed?
                      const isCommitted = tEdits.IsCommitted ?? t.IsCommitted ?? false;

                      // Calculate total cost
                      const totalCost = calcTotalCost(t, tEdits);

                      // Convert numeric county code for each row to its name:
                      const countyName = getCountyName(t.Cnty);

                      return (
                        <tr key={t.TreatmentId || t.TreatmentID}>
                          {/* Committed Checkbox */}
                          <td style={styles.cell}>
                            <input
                              type="checkbox"
                              checked={isCommitted}
                              onChange={(e) =>
                                this.handleTreatmentInputChange(
                                  t.TreatmentId || t.TreatmentID,
                                  'IsCommitted',
                                  e.target.checked
                                )
                              }
                            />
                          </td>

                          {/* Project ID */}
                          <td style={styles.smallerCell}>
                            <input
                              type="text"
                              readOnly
                              style={styles.readOnlyInput}
                              value={t.ProjId || t.ProjectID}
                            />
                          </td>

                          {/* Asset */}
                          <td style={styles.smallerCell}>
                            <input
                              type="text"
                              readOnly
                              style={styles.readOnlyInput}
                              value={getAssetTypeLabel(t.TreatType || t.AssetType || '')}
                            />
                          </td>

                          {/* County name */}
                          <td style={styles.smallerCell}>
                            <input
                              type="text"
                              readOnly
                              style={styles.readOnlyInput}
                              value={countyName}
                            />
                          </td>

                          {/* Route */}
                          <td style={styles.smallerCell}>
                            <input
                              type="text"
                              readOnly
                              style={styles.readOnlyInput}
                              value={(t.Rte || t.Route)?.toString() || ''}
                            />
                          </td>

                          {/* Section */}
                          <td style={styles.smallerCell}>
                            <input
                              type="text"
                              readOnly
                              style={styles.readOnlyInput}
                              value={`${t.FromSection ?? ''}-${t.ToSection ?? ''}`}
                            />
                          </td>

                          {/* BRKEY (was BridgeID) */}
                          <td style={styles.mediumCell}>
                            <input
                              type="text"
                              readOnly
                              style={styles.readOnlyInput}
                              // If your data uses t.BRKEY, or still t.BRIDGE_ID or t.BridgeID:
                              value={t.BRKEY || t.BridgeID || t.BRIDGE_ID || ''}
                            />
                          </td>

                          {/* MPMS ID */}
                          <td style={styles.cell}>
                            <input
                              type="text"
                              style={styles.editableInput}
                              value={tEdits.MPMSID ?? t.MPMSID ?? ''}
                              onChange={(e) =>
                                this.handleTreatmentInputChange(
                                  t.TreatmentId || t.TreatmentID,
                                  'MPMSID',
                                  e.target.value
                                )
                              }
                            />
                          </td>

                          {/* Treat Type */}
                          <td style={styles.cell}>
                            <input
                              type="text"
                              style={styles.editableInput}
                              value={getAssetTypeLabel(
                                tEdits.TreatmentType ??
                                  (t.TreatType || t.TreatmentType) ??
                                  ''
                              )}
                              onChange={(e) =>
                                this.handleTreatmentInputChange(
                                  t.TreatmentId || t.TreatmentID,
                                  'TreatmentType',
                                  e.target.value
                                )
                              }
                            />
                          </td>

                          {/* Treatment */}
                          <td style={styles.cell}>
                            <input
                              type="text"
                              style={styles.editableInput}
                              value={tEdits.Treatment ?? t.Treatment ?? ''}
                              onChange={(e) =>
                                this.handleTreatmentInputChange(
                                  t.TreatmentId || t.TreatmentID,
                                  'Treatment',
                                  e.target.value
                                )
                              }
                            />
                          </td>

                          {/* PreferredYear */}
                          <td style={styles.smallCell}>
                            <input
                              type="number"
                              style={styles.editableInput}
                              value={tEdits.PreferredYear ?? t.PreferredYear ?? ''}
                              onChange={(e) => {
                                const val = parseInt(e.target.value, 10);
                                this.handleTreatmentInputChange(
                                  t.TreatmentId || t.TreatmentID,
                                  'PreferredYear',
                                  val
                                );
                              }}
                            />
                          </td>

                          {/* MinYear (disabled if committed) */}
                          <td style={styles.smallCell}>
                            <input
                              type="number"
                              style={styles.editableInput}
                              readOnly={isCommitted}
                              value={tEdits.MinYear ?? t.MinYear ?? ''}
                              onChange={(e) => {
                                const val = parseInt(e.target.value, 10);
                                this.handleTreatmentInputChange(
                                  t.TreatmentId || t.TreatmentID,
                                  'MinYear',
                                  val
                                );
                              }}
                            />
                          </td>

                          {/* MaxYear (disabled if committed) */}
                          <td style={styles.smallCell}>
                            <input
                              type="number"
                              style={styles.editableInput}
                              readOnly={isCommitted}
                              value={tEdits.MaxYear ?? t.MaxYear ?? ''}
                              onChange={(e) => {
                                const val = parseInt(e.target.value, 10);
                                this.handleTreatmentInputChange(
                                  t.TreatmentId || t.TreatmentID,
                                  'MaxYear',
                                  val
                                );
                              }}
                            />
                          </td>

                          {/* Benefit (rounded to nearest dollar) */}
                          <td style={styles.cell}>
                            <input
                              type="text"
                              style={styles.editableInput}
                              value={formatCurrencyNoDecimals(
                                (tEdits.Benefit ?? t.Benefit ?? 0) as number
                              )}
                              onChange={(e) => {
                                const val = parseCurrencyInput(e.target.value);
                                this.handleTreatmentInputChange(
                                  t.TreatmentId || t.TreatmentID,
                                  'Benefit',
                                  val
                                );
                              }}
                            />
                          </td>

                          {/* Total Cost (read-only) */}
                          <td style={styles.cell}>
                            <input
                              type="text"
                              readOnly
                              style={styles.readOnlyInput}
                              value={formatCurrencyNoDecimals(totalCost)}
                            />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            );
          })}
        </div>

        {/* Buttons at the bottom */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px' }}>
          <button onClick={this.submitScenario} style={{ flex: 1, marginRight: '10px' }}>
            Run Scenario
          </button>
          <button
            onClick={this.saveScenario} // Ensure saveScenario is defined
            disabled={this.state.isSaveDisabled} // A state property controlling Save button
            style={{
              flex: 1,
              backgroundColor: this.state.isSaveDisabled ? 'grey' : 'initial',
              cursor: this.state.isSaveDisabled ? 'not-allowed' : 'pointer'
            }}
          >
            Save Scenario
          </button>
        </div>
      </div>
    );
  }
}

const styles: { [key: string]: React.CSSProperties } = {
  headerRow: { backgroundColor: '#eee' },
  cell: {
    border: '1px solid #ccc',
    padding: '8px',
    textAlign: 'left'
  },
  smallCell: {
    border: '1px solid #ccc',
    padding: '8px',
    textAlign: 'left',
    width: '80px'
  },
  smallerCell: {
    border: '1px solid #ccc',
    padding: '8px',
    textAlign: 'left',
    width: '60px'
  },
  mediumCell: {
    border: '1px solid #ccc',
    padding: '8px',
    textAlign: 'left',
    width: '120px'
  },
  readOnlyInput: {
    width: '100%',
    backgroundColor: '#eee',
    border: 'none',
    textAlign: 'left'
  },
  editableInput: {
    width: '100%',
    textAlign: 'left'
  }
};
