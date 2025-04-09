/** @jsx jsx */
import { React, AllWidgetProps, jsx } from 'jimu-core';
import { JimuMapViewComponent, JimuMapView } from 'jimu-arcgis';
import Select from 'react-select';
import FeatureLayer from 'esri/layers/FeatureLayer';
// If you still need eventEmitter, import it. 
// import eventEmitter from '../../../PennRoadSegments/src/singleton/EventEmitterInstance'; 
import defaultScenarioData from '../data/scenario.json';

interface OptionType {
  value: string;
  label: string;
}

interface State {
  scenario: any;
  jimuMapView: JimuMapView | null;
  featureLayer: FeatureLayer | null;
  projectYears: OptionType[];
  assetTypes: OptionType[];
  treatments: OptionType[];
  routes: OptionType[];
  selectedProjectYears: OptionType[];
  selectedAssetTypes: OptionType[];
  selectedTreatments: OptionType[];
  selectedRoutes: OptionType[];
  users: Array<{ id: number; name: string }>;
  selectedUser: number | null;
  scenarios: Array<{ id: number; name: string }>;
  selectedScenario: number | null;
}

export default class RoadSegmentsFilter extends React.PureComponent<AllWidgetProps<unknown>, State> {
  constructor(props: AllWidgetProps<unknown>) {
    super(props);
    this.state = {
      scenario: defaultScenarioData,
      jimuMapView: null,
      featureLayer: null,
      projectYears: [],
      assetTypes: [],
      treatments: [],
      routes: [],
      selectedProjectYears: [],
      selectedAssetTypes: [],
      selectedTreatments: [],
      selectedRoutes: [],
      users: [],
      selectedUser: null,
      scenarios: [],
      selectedScenario: null
    };
  }

  // Fetch the list of users from GetUsers API
  fetchUsers = async () => {
    try {
      const resp = await fetch('https://demo.pbweb.info/api/GetUsers');
      const users = await resp.json();
      this.setState({ users });
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  // Fetch scenarios for a given user ID from GetScenarios API
  fetchScenarios = async (userId: number) => {
    try {
      const resp = await fetch(`https://demo.pbweb.info/api/GetScenarios?UserId=${userId}`);
      const scenarios = await resp.json();
      this.setState({ scenarios });
    } catch (error) {
      console.error('Error fetching scenarios:', error);
    }
  };

  // Handler for when a user is selected from the dropdown
  handleUserSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    // e.target.value will now be the numeric userId (as a string)
    const userId = parseInt(e.target.value, 10); // e.g. "52" => 52
    this.setState({ selectedUser: userId, scenarios: [], selectedScenario: null });
    this.fetchScenarios(userId);
  };

  // Handler for when a scenario is selected from the dropdown
  handleScenarioSelect = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const scenarioId = parseInt(e.target.value, 10);
    this.setState({ selectedScenario: scenarioId });
    try {
      const resp = await fetch(`https://demo.pbweb.info/api/GetMapJSON?ScenID=${scenarioId}`);
      const newScenario = await resp.json();
      //console.log('GetMapJSON =>', newScenario);
      // Dispatch the scenario-changed event so other widgets update:
      const evt = new CustomEvent('scenario-changed', {
        detail: { scenario: newScenario }
      });
      window.dispatchEvent(evt);
    } catch (error) {
      console.error('Error fetching scenario JSON:', error);
    }
  };

  componentDidMount() {
    if (this.state.jimuMapView) {
      this.initialize();
    }
    window.addEventListener('scenario-changed', this.onScenarioChanged);

    // NEW: Fetch the list of users when the widget mounts
    this.fetchUsers();
  }

  componentWillUnmount() {
    window.removeEventListener('scenario-changed', this.onScenarioChanged);
  }

  componentDidUpdate(prevProps: AllWidgetProps<unknown>, prevState: State) {
    // If the map view changed
    if (this.state.jimuMapView !== prevState.jimuMapView && this.state.jimuMapView) {
      this.initialize();
    }
  }

  // Fired when a new scenario is imported or otherwise set
  onScenarioChanged = (evt: any) => {
    const newScenario = evt.detail.scenario;
    if (!newScenario) return;

    console.log('FilteringWidget: New scenario detected, reloading filters.');

    // Clear out any existing selections
    this.setState(
      {
        scenario: newScenario,
        selectedProjectYears: [],
        selectedAssetTypes: [],
        selectedTreatments: [],
        selectedRoutes: []
      },
      () => {
        this.getUniqueValues(); // Rebuild filter lists from new scenario
      }
    );
  };

  initialize = () => {
    const checkLayer = () => {
      const map = this.state.jimuMapView?.view.map;
      if (!map) {
        console.warn('Map is not available yet.');
        return;
      }
      const featureLayer = map.findLayerById('ScenarioTreatmentsLayer') as FeatureLayer;
      if (featureLayer) {
        this.setState({ featureLayer }, () => {
          // Once the layer is found, build filter lists from the scenario
          this.getUniqueValues();
        });
      } else {
        setTimeout(checkLayer, 500);
      }
    };
    checkLayer();
  };

  // Build filter dropdown lists from the scenario in state
  getUniqueValues = () => {
    const { scenario } = this.state;
    if (!scenario || !scenario.Treatments) return;

    const treatments = scenario.Treatments;

    const yearSet = new Set<string>();
    const assetTypeSet = new Set<string>();
    const treatmentSet = new Set<string>();
    const routeSet = new Set<string>();

    treatments.forEach((t: any) => {
      if (t.Year != null) {
        yearSet.add(String(t.Year));
      }
      if (t.TreatType || t.AssetType) {
        assetTypeSet.add((t.TreatType || t.AssetType).trim());
      }
      if (t.Treatment) {
        treatmentSet.add(t.Treatment.trim());
      }
      if (t.Rte || t.Route) {
        routeSet.add(String(t.Rte || t.Route));
      }
    });

    const projectYears = Array.from(yearSet).sort().map((y) => ({ value: y, label: y }));
    const assetTypes = Array.from(assetTypeSet).sort().map((at) => ({ value: at, label: at }));
    const treatmentsOptions = Array.from(treatmentSet).sort().map((tr) => ({ value: tr, label: tr }));
    const routes = Array.from(routeSet).sort().map((r) => ({ value: r, label: r }));

    this.setState({
      projectYears,
      assetTypes,
      treatments: treatmentsOptions,
      routes
    });
  };

  onActiveViewChange = (jimuMapView: JimuMapView) => {
    if (jimuMapView) {
      this.setState({ jimuMapView }, () => {
        console.log('MapView updated');
        this.initialize();
      });
    } else {
      this.setState({ jimuMapView: null, featureLayer: null });
    }
  };

  handleFilterChange = (stateKey: keyof State, selectedOptions: OptionType[]) => {
    //console.log(`handleFilterChange => stateKey: ${stateKey}`, selectedOptions);
    this.setState({ [stateKey]: selectedOptions } as Pick<State, keyof State>, () => {
      this.applyFilter();
    });
  };

  isFilterActive = (filterKey: keyof State): boolean => {
    const values = this.state[filterKey] as OptionType[];
    return values.length > 0;
  };

  clearAllFilters = () => {
    this.setState(
      {
        selectedProjectYears: [],
        selectedAssetTypes: [],
        selectedTreatments: [],
        selectedRoutes: []
      },
      this.applyFilter
    );
  };

  applyFilter = () => {
    const {
      scenario,
      featureLayer,
      selectedProjectYears,
      selectedAssetTypes,
      selectedTreatments,
      selectedRoutes
    } = this.state;

    if (!scenario || !scenario.Treatments) return;
    if (!featureLayer) return;

    // Build the definition expression for the map layer
    const whereClauses: string[] = [];

    // Year Filter
    if (selectedProjectYears.length > 0) {
      const yearVals = selectedProjectYears.map((opt) => +opt.value);
      whereClauses.push(`Year IN (${yearVals.join(',')})`);
    }

    // AssetType Filter
    if (selectedAssetTypes.length > 0) {
      const assetVals = selectedAssetTypes.map((opt) => `'${opt.value.replace(/'/g, "''")}'`);
      whereClauses.push(`AssetType IN (${assetVals.join(',')})`);
    }

    // Treatment Filter
    if (selectedTreatments.length > 0) {
      const treatVals = selectedTreatments.map((opt) => `'${opt.value.replace(/'/g, "''")}'`);
      whereClauses.push(`Treatment IN (${treatVals.join(',')})`);
    }

    // Route Filter
    if (selectedRoutes.length > 0) {
      const routeVals = selectedRoutes.map((opt) => +opt.value);
      whereClauses.push(`Route IN (${routeVals.join(',')})`);
    }

    // Set the layer's definition expression so the map is filtered
    featureLayer.definitionExpression = whereClauses.join(' AND ');
    //console.log('Updated Definition Expression:', featureLayer.definitionExpression);

    // Switch to cost-based symbology if we have any filter active
    const useCostBased = whereClauses.length > 0;
    window.dispatchEvent(
      new CustomEvent('symbologyUpdate', {
        detail: { useCostBasedSymbology: useCostBased }
      })
    );

    // Now figure out which TREATMENTS pass the filter (for the InfoPanel)
    const matchedTreatments = scenario.Treatments.filter((t: any) => {
      const yearOk =
        !selectedProjectYears.length ||
        selectedProjectYears.some((opt) => +opt.value === t.Year);

      const assetOk =
        !selectedAssetTypes.length ||
        selectedAssetTypes.some((opt) => opt.value === (t.TreatType || t.AssetType));

      const treatOk =
        !selectedTreatments.length ||
        selectedTreatments.some((opt) => opt.value === t.Treatment);

      const routeOk =
        !selectedRoutes.length ||
        selectedRoutes.some((opt) => +opt.value === (t.Rte || t.Route));

      return yearOk && assetOk && treatOk && routeOk;
    });

    // Collect the unique treatment IDs
    const filteredTreatIds = matchedTreatments.map(
      (t: any) => t.TreatId ?? t.TreatmentId ?? t.TreatmentID
    );

    // Also figure out which project IDs those treatments belong to
    const filteredProjIds = new Set<number>();
    matchedTreatments.forEach((t: any) => {
      const pid = t.ProjId ?? t.ProjectID;
      if (pid != null) filteredProjIds.add(pid);
    });

    // Emit an event so the InfoPanel can display only these items
    const evt = new CustomEvent('filter-updated', {
      detail: {
        filteredProjIds: Array.from(filteredProjIds),
        filteredTreatIds
      }
    });
    window.dispatchEvent(evt);
  };

  render() {
    const {
      projectYears,
      assetTypes,
      treatments,
      routes,
      selectedProjectYears,
      selectedAssetTypes,
      selectedTreatments,
      selectedRoutes,
      users,
      selectedUser,
      scenarios,
      selectedScenario
    } = this.state;
  
    return (
      <div
        className="widget-road-segments-filter"
        style={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'flex-start',
          justifyContent: 'space-around',
          padding: '4px',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          flexWrap: 'wrap'
        }}
      >
        {/* User dropdown with darker background */}
        <div
          style={{
            margin: '6px',
            minWidth: '130px',
            backgroundColor: '#e0e0e0',
            borderRadius: '4px',
            padding: '4px'
          }}
        >
          <label style={{ display: 'block', marginBottom: '3px', fontWeight: 'normal' }}>
            Select User
          </label>
          <select
            value={selectedUser ?? ''}
            onChange={this.handleUserSelect}
            style={{ width: '100%', padding: '4px', fontSize: '0.9em' }}
          >
            <option value="">-- Select User --</option>
            {users.map((u) => (
              <option key={u.userId} value={u.userId}>
                {u.name}
              </option>
            ))}
          </select>
        </div>
  
        {/* Scenario dropdown with darker background */}
        <div
          style={{
            margin: '6px',
            minWidth: '130px',
            backgroundColor: '#e0e0e0',
            borderRadius: '4px',
            padding: '4px'
          }}
        >
          <label style={{ display: 'block', marginBottom: '3px', fontWeight: 'normal' }}>
            Select Scenario
          </label>
          <select
            value={selectedScenario ?? ''}
            onChange={this.handleScenarioSelect}
            style={{ width: '100%', padding: '4px', fontSize: '0.9em' }}
          >
            <option value="">-- Select Scenario --</option>
            {scenarios.map((s) => (
              <option key={s.scenarioId} value={s.scenarioId}>
                {s.scenarioName}
              </option>
            ))}
          </select>
        </div>
  
        {/* Year Filter */}
        <div style={{ margin: '6px', minWidth: '120px' }}>
          <label
            htmlFor="projectYear"
            style={{
              display: 'block',
              marginBottom: '3px',
              fontWeight: this.isFilterActive('selectedProjectYears') ? 'bold' : 'normal',
              color: this.isFilterActive('selectedProjectYears') ? 'blue' : 'inherit'
            }}
          >
            Year
          </label>
          <Select
            id="projectYear"
            isMulti
            options={projectYears}
            value={selectedProjectYears}
            onChange={(opts) => this.handleFilterChange('selectedProjectYears', opts)}
            placeholder="Select Year(s)"
            /* Ensure dropdown is rendered above the map */
            menuPortalTarget={document.body}
            menuPosition="fixed"
            styles={{
              control: (provided) => ({
                ...provided,
                minHeight: '30px',
                fontSize: '0.9em'
              }),
              menu: (provided) => ({
                ...provided,
                zIndex: 9999
              }),
              multiValue: (provided) => ({
                ...provided,
                backgroundColor: 'lightblue'
              })
            }}
          />
        </div>
  
        {/* Asset Type Filter */}
        <div style={{ margin: '6px', minWidth: '120px' }}>
          <label
            htmlFor="assetType"
            style={{
              display: 'block',
              marginBottom: '3px',
              fontWeight: this.isFilterActive('selectedAssetTypes') ? 'bold' : 'normal',
              color: this.isFilterActive('selectedAssetTypes') ? 'blue' : 'inherit'
            }}
          >
            Asset Type
          </label>
          <Select
            id="assetType"
            isMulti
            options={assetTypes}
            value={selectedAssetTypes}
            onChange={(opts) => this.handleFilterChange('selectedAssetTypes', opts)}
            placeholder="Select Asset(s)"
            menuPortalTarget={document.body}
            menuPosition="fixed"
            styles={{
              control: (provided) => ({
                ...provided,
                minHeight: '30px',
                fontSize: '0.9em'
              }),
              menu: (provided) => ({
                ...provided,
                zIndex: 9999
              }),
              multiValue: (provided) => ({
                ...provided,
                backgroundColor: 'lightblue'
              })
            }}
          />
        </div>
  
        {/* Treatment Filter */}
        <div style={{ margin: '6px', minWidth: '120px' }}>
          <label
            htmlFor="treatment"
            style={{
              display: 'block',
              marginBottom: '3px',
              fontWeight: this.isFilterActive('selectedTreatments') ? 'bold' : 'normal',
              color: this.isFilterActive('selectedTreatments') ? 'blue' : 'inherit'
            }}
          >
            Treatment
          </label>
          <Select
            id="treatment"
            isMulti
            options={treatments}
            value={selectedTreatments}
            onChange={(opts) => this.handleFilterChange('selectedTreatments', opts)}
            placeholder="Select Treatment(s)"
            menuPortalTarget={document.body}
            menuPosition="fixed"
            styles={{
              control: (provided) => ({
                ...provided,
                minHeight: '30px',
                fontSize: '0.9em'
              }),
              menu: (provided) => ({
                ...provided,
                zIndex: 9999
              }),
              multiValue: (provided) => ({
                ...provided,
                backgroundColor: 'lightblue'
              })
            }}
          />
        </div>
  
        {/* Route Filter */}
        <div style={{ margin: '6px', minWidth: '120px' }}>
          <label
            htmlFor="route"
            style={{
              display: 'block',
              marginBottom: '3px',
              fontWeight: this.isFilterActive('selectedRoutes') ? 'bold' : 'normal',
              color: this.isFilterActive('selectedRoutes') ? 'blue' : 'inherit'
            }}
          >
            Route
          </label>
          <Select
            id="route"
            isMulti
            options={routes}
            value={selectedRoutes}
            onChange={(opts) => this.handleFilterChange('selectedRoutes', opts)}
            placeholder="Select Route(s)"
            menuPortalTarget={document.body}
            menuPosition="fixed"
            styles={{
              control: (provided) => ({
                ...provided,
                minHeight: '30px',
                fontSize: '0.9em'
              }),
              menu: (provided) => ({
                ...provided,
                zIndex: 9999
              }),
              multiValue: (provided) => ({
                ...provided,
                backgroundColor: 'lightblue'
              })
            }}
          />
        </div>
  
        {/* Clear All Filters */}
        <div style={{ margin: '6px', alignSelf: 'center' }}>
          <button onClick={this.clearAllFilters} style={{ padding: '4px 8px', fontSize: '0.85em' }}>
            Clear All Filters
          </button>
        </div>
  
        {/* Hidden MapViewComponent so we can access the map */}
        {this.props.useMapWidgetIds?.length ? (
          <div style={{ display: 'none' }}>
            <JimuMapViewComponent
              useMapWidgetId={this.props.useMapWidgetIds[0]}
              onActiveViewChange={this.onActiveViewChange}
            />
          </div>
        ) : null}
      </div>
    );
  }  
}
