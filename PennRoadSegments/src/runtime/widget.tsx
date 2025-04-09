/** @jsx jsx */
import { React, AllWidgetProps, jsx } from 'jimu-core';
import { JimuMapViewComponent, JimuMapView } from 'jimu-arcgis';
import eventEmitter from '../singleton/EventEmitterInstance';
import FeatureLayer from 'esri/layers/FeatureLayer';
import Graphic from 'esri/Graphic';
import Polyline from 'esri/geometry/Polyline';
import * as projection from 'esri/geometry/projection';
import * as geometryEngine from 'esri/geometry/geometryEngine';

// Load a default scenario JSON as fallback
import defaultScenarioData from '../data/scenario.json';

console.log("PennRoadSegments: eventEmitter path =", require.resolve('../singleton/EventEmitterInstance'));

// Segment Treatment Styles from configLayerStyles.js script. Retired.
const segmentTreatmentStyles = {
  "Bituminous Overlay": {
    "color": "rgba(107,14,62,1)"
  },
  "Bridge Replacement": {
    "color": "rgba(139,14,94,1)"
  },
  "CommittedTreatmentType": {
    "color": "rgba(153,98,156,1)"
  },
  "Culvert Rehab (Other)": {
    "color": "rgba(151,165,226,1)"
  },
  "Culvert Replacement (Box/Frame/Arch)": {
    "color": "rgba(151,165,226,1)"
  },
  "Culvert Replacement (Other)": {
    "color": "rgba(151,165,226,1)"
  },
  "Culvert Replacement (Pipe)": {
    "color": "rgba(151,165,226,1)"
  },
  "Deck Replacement": {
    "color": "rgba(140,206,248,1)"
  },
  "Epoxy/Joint Glands/Coatings": {
    "color": "rgba(132,233,239,1)"
  },
  "H1": {
    "color": "rgba(34,234,34,1)"
  },
  "H10": {
    "color": "rgba(34,234,34,1)"
  },
  "H11": {
    "color": "rgba(34,234,34,1)"
  },
  "H12": {
    "color": "rgba(34,234,34,1)"
  },
  "H13": {
    "color": "rgba(34,234,34,1)"
  },
  "H14": {
    "color": "rgba(34,234,34,1)"
  },
  "H15": {
    "color": "rgba(34,234,34,1)"
  },
  "H16": {
    "color": "rgba(34,234,34,1)"
  },
  "H16+H4": {
    "color": "rgba(34,234,34,1)"
  },
  "H17": {
    "color": "rgba(34,234,34,1)"
  },
  "H18": {
    "color": "rgba(34,234,34,1)"
  },
  "H19": {
    "color": "rgba(34,234,34,1)"
  },
  "H2": {
    "color": "rgba(34,234,34,1)"
  },
  "H20": {
    "color": "rgba(34,234,34,1)"
  },
  "H21": {
    "color": "rgba(34,234,34,1)"
  },
  "H22": {
    "color": "rgba(34,234,34,1)"
  },
  "H23": {
    "color": "rgba(34,234,34,1)"
  },
  "H3": {
    "color": "rgba(34,234,34,1)"
  },
  "H4": {
    "color": "rgba(34,234,34,1)"
  },
  "H5": {
    "color": "rgba(34,234,34,1)"
  },
  "H6": {
    "color": "rgba(34,234,34,1)"
  },
  "H7": {
    "color": "rgba(34,234,34,1)"
  },
  "H8": {
    "color": "rgba(34,234,34,1)"
  },
  "H9": {
    "color": "rgba(34,234,34,1)"
  },
  "J1": {
    "color": "rgba(207,251,114,1)"
  },
  "J10": {
    "color": "rgba(207,251,114,1)"
  },
  "J11": {
    "color": "rgba(207,251,114,1)"
  },
  "J11+J9": {
    "color": "rgba(207,251,114,1)"
  },
  "J12": {
    "color": "rgba(207,251,114,1)"
  },
  "J13": {
    "color": "rgba(207,251,114,1)"
  },
  "J14": {
    "color": "rgba(207,251,114,1)"
  },
  "J14+J1": {
    "color": "rgba(207,251,114,1)"
  },
  "J14+J9": {
    "color": "rgba(207,251,114,1)"
  },
  "J15": {
    "color": "rgba(207,251,114,1)"
  },
  "J16": {
    "color": "rgba(207,251,114,1)"
  },
  "J17": {
    "color": "rgba(207,251,114,1)"
  },
  "J17+J12": {
    "color": "rgba(207,251,114,1)"
  },
  "J17+J9": {
    "color": "rgba(207,251,114,1)"
  },
  "J18": {
    "color": "rgba(207,251,114,1)"
  },
  "J19": {
    "color": "rgba(207,251,114,1)"
  },
  "J2": {
    "color": "rgba(207,251,114,1)"
  },
  "J20": {
    "color": "rgba(207,251,114,1)"
  },
  "J21": {
    "color": "rgba(207,251,114,1)"
  },
  "J21+J12": {
    "color": "rgba(207,251,114,1)"
  },
  "J21+J15": {
    "color": "rgba(207,251,114,1)"
  },
  "J21+J7": {
    "color": "rgba(207,251,114,1)"
  },
  "J21+J8": {
    "color": "rgba(207,251,114,1)"
  },
  "J21+J9": {
    "color": "rgba(207,251,114,1)"
  },
  "J22": {
    "color": "rgba(207,251,114,1)"
  },
  "J22+J12": {
    "color": "rgba(207,251,114,1)"
  },
  "J22+J8": {
    "color": "rgba(207,251,114,1)"
  },
  "J22+J9": {
    "color": "rgba(207,251,114,1)"
  },
  "J23": {
    "color": "rgba(207,251,114,1)"
  },
  "J23+J12": {
    "color": "rgba(207,251,114,1)"
  },
  "J23+J9": {
    "color": "rgba(207,251,114,1)"
  },
  "J24": {
    "color": "rgba(207,251,114,1)"
  },
  "J24+J12": {
    "color": "rgba(207,251,114,1)"
  },
  "J24+J9": {
    "color": "rgba(207,251,114,1)"
  },
  "J25": {
    "color": "rgba(207,251,114,1)"
  },
  "J25+J12": {
    "color": "rgba(207,251,114,1)"
  },
  "J25+J15": {
    "color": "rgba(207,251,114,1)"
  },
  "J25+J4": {
    "color": "rgba(207,251,114,1)"
  },
  "J25+J7": {
    "color": "rgba(207,251,114,1)"
  },
  "J25+J8": {
    "color": "rgba(207,251,114,1)"
  },
  "J25+J9": {
    "color": "rgba(207,251,114,1)"
  },
  "J26": {
    "color": "rgba(207,251,114,1)"
  },
  "J26+J12": {
    "color": "rgba(207,251,114,1)"
  },
  "J26+J7": {
    "color": "rgba(207,251,114,1)"
  },
  "J26+J8": {
    "color": "rgba(207,251,114,1)"
  },
  "J26+J9": {
    "color": "rgba(207,251,114,1)"
  },
  "J27": {
    "color": "rgba(207,251,114,1)"
  },
  "J3": {
    "color": "rgba(207,251,114,1)"
  },
  "J4": {
    "color": "rgba(207,251,114,1)"
  },
  "J5": {
    "color": "rgba(207,251,114,1)"
  },
  "J6": {
    "color": "rgba(207,251,114,1)"
  },
  "J7": {
    "color": "rgba(207,251,114,1)"
  },
  "J8": {
    "color": "rgba(207,251,114,1)"
  },
  "J9": {
    "color": "rgba(207,251,114,1)"
  },
  "Latex/Joints/Coatings": {
    "color": "rgba(255,255,0,1)"
  },
  "No Treatment": {
    "color": "rgba(156,156,156,1)"
  },
  "Overlay": {
    "color": "rgba(251,217,94,1)"
  },
  "Painting (Full)": {
    "color": "rgba(240,126,45,1)"
  },
  "Painting (Joint/Spot/Zone)": {
    "color": "rgba(240,126,45,1)"
  },
  "Substructure Rehab": {
    "color": "rgba(230,0,0,1)"
  },
  "Superstructure Rep/Rehab": {
    "color": "rgba(230,0,169,1)"
  },
  "Structural Overlay/Joints/Coatings": {
    "color": "rgba(230,127,220,1)"
  },
};

interface State {
  jimuMapView: JimuMapView | null;
  useCostBasedSymbology: boolean;
  scenarioData: any;
  runComplete: boolean;
}

export default class PennRoadSegments extends React.PureComponent<AllWidgetProps<unknown>, State> {
  featureLayer: FeatureLayer;
  fileInputRef: React.RefObject<HTMLInputElement>;
  selectedFeature: __esri.Graphic | null = null;
  statusInterval: any = null;

  constructor(props: AllWidgetProps<unknown>) {
    super(props);
    this.state = {
      jimuMapView: null,
      useCostBasedSymbology: false,
      scenarioData: defaultScenarioData,
      runComplete: false
    };
    this.fileInputRef = React.createRef();
    this.featureLayer = new FeatureLayer({
      title: 'Scenario Treatments',
      id: 'ScenarioTreatmentsLayer',
      visible: true,
      objectIdField: 'OBJECTID',
      geometryType: 'polyline',
      spatialReference: { wkid: 102100 },
      fields: [
        { name: 'OBJECTID', type: 'oid' },
        { name: 'ProjectID', type: 'integer' },
        { name: 'SystemID', type: 'integer' },
        { name: 'TreatmentID', type: 'string' },
        { name: 'AssetType', type: 'string' },
        { name: 'Route', type: 'integer' },
        { name: 'SectionFrom', type: 'integer' },
        { name: 'SectionTo', type: 'integer' },
        { name: 'BridgeID', type: 'string' },
        { name: 'TreatmentType', type: 'string' },
        { name: 'Treatment', type: 'string' },
        { name: 'Year', type: 'integer' },
        { name: 'DirectCost', type: 'double' },
        { name: 'DesignCost', type: 'double' },
        { name: 'ROWCost', type: 'double' },
        { name: 'UtilCost', type: 'double' },
        { name: 'OtherCost', type: 'double' }
      ],
      popupTemplate: {
        title: 'Treatment: {Treatment}',
        content: [
          {
            type: 'fields',
            fieldInfos: [
              { fieldName: 'ProjectID', label: 'Project ID' },
              { fieldName: 'SystemID', label: 'System ID' },
              { fieldName: 'TreatmentID', label: 'Treatment ID' },
              { fieldName: 'AssetType', label: 'Asset Type' },
              { fieldName: 'Route', label: 'Route' },
              { fieldName: 'SectionFrom', label: 'Section From' },
              { fieldName: 'SectionTo', label: 'Section To' },
              { fieldName: 'BridgeID', label: 'Bridge ID' },
              { fieldName: 'TreatmentType', label: 'Treatment Type' },
              { fieldName: 'Year', label: 'Year' },
              { fieldName: 'DirectCost', label: 'Direct Cost' },
              { fieldName: 'DesignCost', label: 'Design Cost' },
              { fieldName: 'ROWCost', label: 'ROW Cost' },
              { fieldName: 'UtilCost', label: 'Util Cost' },
              { fieldName: 'OtherCost', label: 'Other Cost' }
            ]
          }
        ]
      }
    });
    this.featureLayer.outFields = ['*'];
    this.featureLayer.popupEnabled = true;
    this.featureLayer.elevationInfo = { mode: 'on-the-ground' };
    this.featureLayer.renderer = this.getRenderer();
  }

  componentDidMount() {
    window.addEventListener('symbologyUpdate', this.handleSymbologyUpdate);
    window.addEventListener('scenario-changed', this.handleScenarioChanged);
  
    // Listen for scenario-submitted events from InfoPanel
    window.addEventListener('scenario-submitted', this.onScenarioSubmitted);
  
    // Start polling scenario status every minute (if runComplete=false) commented out to reduce status updates.
    //this.statusInterval = setInterval(() => {
    //  if (!this.state.runComplete) {
    //    this.checkScenarioStatus();
    //  }
    //}, 60000);
  }

  componentWillUnmount() {
    window.removeEventListener('symbologyUpdate', this.handleSymbologyUpdate);
    window.removeEventListener('scenario-changed', this.handleScenarioChanged);
  
    // Remove scenario-submitted listener
    window.removeEventListener('scenario-submitted', this.handleScenarioSubmitted);
  
    if (this.statusInterval) clearInterval(this.statusInterval);
  }

  componentDidUpdate(prevProps: AllWidgetProps<unknown>, prevState: State) {
    if (this.state.jimuMapView !== prevState.jimuMapView && this.state.jimuMapView) {
      this.setupPopupSelection(this.state.jimuMapView.view);
      this.loadDataFromScenario(this.state.scenarioData);
    }
    if (this.state.useCostBasedSymbology !== prevState.useCostBasedSymbology && this.featureLayer) {
      this.featureLayer.renderer = this.getRenderer();
      this.featureLayer.refresh();
    }
  }

  onScenarioSubmitted = () => {
    console.log('PennRoadSegments => scenario re-submitted, resetting poll...');
  
    // We always set runComplete = false to indicate a new run is in progress
    this.setState({ runComplete: false }, () => {
      // Clear the old interval if it exists
      if (this.statusInterval) {
        clearInterval(this.statusInterval);
      }
  
      // Start a new interval: checks HasScenarioRunCompleted every 60s -- moved from componentDidMount
      this.statusInterval = setInterval(() => {
        if (!this.state.runComplete) {
          this.checkScenarioStatus();
        }
      }, 60000);
  
      // Optionally do an immediate check once:
      this.checkScenarioStatus();
    });
  };
  
  checkScenarioStatus = async () => {
    try {
      // If your JSON is guaranteed to have "Scenario" => "ScenId", this is enough:
      //   const scenId = this.state.scenarioData?.Scenario?.ScenId;
      // If it might vary, do a fallback:
      const scenarioObj = this.state.scenarioData?.Scenario || this.state.scenarioData?.scenario || {};
      const scenId = scenarioObj.ScenId ?? scenarioObj.ScenID ?? scenarioObj.ScenarioID ?? scenarioObj.scenId;
      
      if (!scenId) {
        console.warn('No scenario ID found in scenarioData. scenarioObj =', scenarioObj);
        return;
      }
  
      const url = `https://demo.pbweb.info/api/HasScenarioRunCompleted?ScenID=${scenId}`;
      console.log('Checking scenario status =>', url);
  
      const resp = await fetch(url);
      const data = await resp.json();
      console.log('Has Scenario Run Completed =>', data);
  
      // Suppose the API returns { success: boolean, notes: string }
      if (data.success === true && data.notes?.toLowerCase() === 'success') {
        if (this.statusInterval) {
          clearInterval(this.statusInterval);
          this.statusInterval = null;
        }
        this.setState({ runComplete: true }, () => {
          console.log('Scenario run is completed, refresh map is now enabled.');
          // Now the user can manually click "Refresh Map" if they want
        });
      } else {
        console.log('Scenario run not completed yet or notes != "success".');
      }
    } catch (err) {
      console.error('Error checking scenario status:', err);
    }
  };

  refreshMapData = async () => {
    try {
      const scenarioObj = this.state.scenarioData?.Scenario || this.state.scenarioData?.scenario || {};
      const scenId = scenarioObj.ScenId ?? scenarioObj.ScenID ?? scenarioObj.ScenarioID ?? scenarioObj.scenId;
      if (!scenId) {
        console.warn('No Scenario ID found in scenarioData; cannot refresh map.');
        return;
      }
      const url = `https://demo.pbweb.info/api/GetMapJSON?ScenID=${scenId}`;
      console.log('Fetching updated scenario =>', url);
      const resp = await fetch(url);
      const newScenario = await resp.json();
      //console.log('GetMapJSON =>', newScenario);
      // Dispatch scenario-changed so all widgets pick up the new scenario
      const evt = new CustomEvent('scenario-changed', {
        detail: { scenario: newScenario }
      });
      window.dispatchEvent(evt);
      // After a successful refresh, disable the Refresh Map button by resetting runComplete
      this.setState({ scenarioData: newScenario, runComplete: false });
    } catch (err) {
      console.error('Error refreshing map data:', err);
    }
  };

  handleSymbologyUpdate = (evt: any) => {
    this.setState({ useCostBasedSymbology: evt.detail.useCostBasedSymbology });
  };

  handleScenarioChanged = (evt: any) => {
    const newScenario = evt.detail.scenario;
    if (!newScenario) return;
    console.log('Road Segments => scenario-changed. Reloading map data...');
    this.setState({ scenarioData: newScenario }, () => {
      if (this.state.jimuMapView) {
        this.loadDataFromScenario(newScenario);
      }
    });
  };

  activeViewChangeHandler = (jmv: JimuMapView) => {
    if (this.state.jimuMapView) {
      this.state.jimuMapView.view.map.remove(this.featureLayer);
    }
    this.setState({ jimuMapView: jmv || null });
  };

  renderImportControls() {
    const onImportClick = () => {
      if (this.fileInputRef.current) {
        this.fileInputRef.current.value = '';
        this.fileInputRef.current.click();
      }
    };

    const onFileSelected = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
    
      try {
        const text = await file.text();
        const parsed = JSON.parse(text);
        console.log('User imported scenario =>', parsed);
    
        // Dispatch the scenario-changed event so the map and other widgets load the new scenario.
        const evt = new CustomEvent('scenario-changed', {
          detail: { scenario: parsed }
        });
        window.dispatchEvent(evt);
    
        // Reset runComplete to false, because a newly imported scenario hasn't been run yet.
        this.setState({ scenarioData: parsed, runComplete: false }, () => {
          if (this.state.jimuMapView) {
            this.loadDataFromScenario(parsed);
          }
        });
      } catch (err) {
        console.error('Error reading scenario file:', err);
      }
    };

    return (
      <div style={{ marginBottom: 8 }}>
        <button onClick={onImportClick} style={{ padding: '5px 10px', marginRight: 8 }}>
          Import Scenario
        </button>
        <input
          type="file"
          accept=".json"
          ref={this.fileInputRef}
          style={{ display: 'none' }}
          onChange={onFileSelected}
        />
        <button onClick={this.refreshMapData} style={{ padding: '5px 10px' }} disabled={!this.state.runComplete}>
          Refresh Map
        </button>
      </div>
    );
  }

  render() {
    return (
      <div style={{ height: '100%', width: '100%', overflow: 'auto' }}>
        {this.renderImportControls()}

        {this.props.useMapWidgetIds && this.props.useMapWidgetIds.length > 0 ? (
          <JimuMapViewComponent
            useMapWidgetId={this.props.useMapWidgetIds[0]}
            onActiveViewChange={this.activeViewChangeHandler}
          />
        ) : (
          <p>Please select a map.</p>
        )}
      </div>
    );
  }

  getRenderer() {
    if (this.state.useCostBasedSymbology) { // Cost-based symbology
      return {
        type: 'class-breaks',
        field: 'DirectCost',
        classBreakInfos: [
          {
            minValue: 0,
            maxValue: 100000,
            symbol: { type: 'simple-line', color: [34, 139, 34], width: 3 },
            label: '< 100k'
          },
          {
            minValue: 100001,
            maxValue: 500000,
            symbol: { type: 'simple-line', color: [144, 238, 144], width: 3 },
            label: '100k - 500k'
          },
          {
            minValue: 500001,
            maxValue: 1000000,
            symbol: { type: 'simple-line', color: [255, 255, 0], width: 3 },
            label: '500k - 1M'
          },
          {
            minValue: 1000001,
            maxValue: 2000000,
            symbol: { type: 'simple-line', color: [255, 165, 0], width: 3 },
            label: '1M - 2M'
          },
          {
            minValue: 2000001,
            maxValue: 5000000,
            symbol: { type: 'simple-line', color: [255, 69, 0], width: 3 },
            label: '2M - 5M'
          },
          {
            minValue: 5000001,
            maxValue: Infinity,
            symbol: { type: 'simple-line', color: [178, 34, 34], width: 3 },
            label: '> 5M'
          }
        ]
      };
    } else {
      const years = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035]; // Styles for year-based symbology--default when map opened
      const blues = [
        [222, 235, 247],
        [198, 219, 239],
        [158, 202, 225],
        [107, 174, 214],
        [66, 146, 198],
        [33, 113, 181],
        [8, 81, 156],
        [8, 48, 107],
        [3, 19, 43]
      ];
      const uniqueValueInfos = years.map((yr, idx) => {
        const colorIndex = idx % blues.length;
        return {
          value: yr,
          symbol: { type: 'simple-line', color: blues[colorIndex], width: 3 },
          label: `${yr}`
        };
      });
      return {
        type: 'unique-value',
        field: 'Year',
        uniqueValueInfos,
        defaultSymbol: { type: 'simple-line', color: [128, 128, 128], width: 2 }
      };
    }
  }

  setupPopupSelection(view: __esri.MapView | __esri.SceneView) {
    if (!view || view.type === '3d') return;
    const mapView = view as __esri.MapView;
    mapView.on('click', async (event) => {
      try {
        const response = await mapView.hitTest(event);
        if (!response.results.length) {
          console.warn('No features detected at click location.');
          return;
        }
        const clickedFeature = response.results.find(
          (r) => r.graphic.layer === this.featureLayer
        )?.graphic;
        if (!clickedFeature) {
          console.warn('No valid feature clicked.');
          return;
        }
        //console.log('Clicked feature FULL attributes:', clickedFeature.attributes);

        let projId =
          clickedFeature.attributes?.ProjId ||
          clickedFeature.attributes?.ProjectID ||
          clickedFeature.attributes?.SchemaId ||
          clickedFeature.attributes?.SystemID;

        if (!projId) {
          console.warn('Clicked feature has no valid ID fields.');
          return;
        }

        console.log('Found ProjectID:', projId);
        const evt = new CustomEvent('segment-selected', {
          detail: { projId: Number(projId) }
        });
        window.dispatchEvent(evt);
      } catch (err) {
        console.error('Error handling segment click:', err);
      }
    });
  }

  getSelectedFeature() {
    return this.selectedFeature;
  }

  loadDataFromScenario(scenario: any) {
    if (!this.state.jimuMapView) {
      console.warn('No JimuMapView available, cannot load scenario yet.');
      return;
    }

    const view = this.state.jimuMapView.view;
    if (!view) return;

    const existingLayer = view.map.findLayerById(this.featureLayer.id);
    if (existingLayer) {
      view.map.remove(existingLayer);
    }

    projection.load().then(() => {
      this._loadTreatments(view, scenario);
    });
  }

  async _loadTreatments(view: __esri.MapView, scenario: any) {
    try {
      view.map.basemap = 'gray-vector';
      const { Projects, Treatments } = scenario;
      if (!Projects || !Treatments) {
        console.warn('Scenario lacks Projects or Treatments array');
        return;
      }
      const graphics: __esri.Graphic[] = [];
      let objectIdCounter = 1;
      const geometriesToProject: { geometry: __esri.Polyline; treatment: any; project: any }[] = [];
      for (const t of Treatments) {
        const projId = t.ProjId || t.ProjectID;
        const foundProject = Projects.find((p: any) => (p.ProjId || p.ProjectID) === projId);
        if (!foundProject) {
          console.warn(`No matching project for Treatment ${t.TreatmentId || t.TreatmentID}, ProjId=${projId}`);
          continue;
        }
        if (!(foundProject.ProjId || foundProject.ProjectID) || !(foundProject.SchemaId || foundProject.SystemID)) {
          console.warn(`Skipping project due to missing identifiers:`, foundProject);
          continue;
        }
        const countyVal = t.Cnty ?? foundProject.County;
        const routeVal = t.Rte ?? t.Route;
        if (!countyVal || !routeVal) {
          console.warn(`Skipping treatment ${t.TreatmentId || t.TreatmentID} due to missing county/route`, { countyVal, routeVal, t });
          continue;
        }
        const fromSec = t.FromSection || t.SectionFrom;
        const toSec = t.ToSection || t.SectionTo;
        if (fromSec == null || toSec == null) {
          console.warn(`Missing section info for treatment ${t.TreatmentId || t.TreatmentID}`, t);
          continue;
        }
        const whereClause = `(
          CTY_CODE='${countyVal.toString().padStart(2, '0')}'
          AND ST_RT_NO='${routeVal.toString().padStart(4, '0')}'
          AND SEG_NO >= '${fromSec.toString().padStart(4, '0')}'
          AND SEG_NO <= '${toSec.toString().padStart(4, '0')}'
        )`;
        console.log(`🔍 Querying for Treatment ${t.TreatmentId || t.TreatmentID}:`, whereClause);
        const params = {
          where: whereClause,
          returnGeometry: true,
          outFields: 'ST_RT_NO,CTY_CODE,DISTRICT_NO,SEG_NO',
          outSR: '4326',
          f: 'json'
        };
        const resp = await fetch(
          'https://gis.penndot.gov/arcgis/rest/services/opendata/roadwaysegments/MapServer/0/query',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams(params)
          }
        );
        const data = await resp.json();
        if (data.error) {
          console.error(`API Error for Treatment ${t.TreatmentId || t.TreatmentID}:`, data.error, 'WhereClause:', whereClause);
          continue;
        }
        if (!data.features || data.features.length === 0) {
          console.warn(`No matching features found for Treatment ${t.TreatmentId || t.TreatmentID}. WhereClause: ${whereClause}`, t);
          continue;
        }
        data.features.forEach((feature: any) => {
          if (!feature.geometry) {
            console.warn('Skipping feature due to missing geometry:', feature);
            return;
          }
          geometriesToProject.push({
            geometry: new Polyline(feature.geometry),
            treatment: t,
            project: foundProject
          });
        });
      }
      if (!geometriesToProject.length) {
        console.warn('No valid geometries found for projection.');
        return;
      }
      await projection.load();
      const projected = projection.project(
        geometriesToProject.map((g) => g.geometry),
        view.spatialReference
      ) as __esri.Polyline[];
      const grouped: { [key: string]: __esri.Polyline[] } = {};
      projected.forEach((geom, idx) => {
        if (!geom) {
          console.warn(`Skipping projected geometry at index ${idx} (undefined)`);
          return;
        }
        const t = geometriesToProject[idx].treatment;
        const treatKey = t.TreatId ?? t.TreatmentId ?? t.TreatmentID;
        const projKey = t.ProjId ?? t.ProjectID;
        const groupKey = `${projKey}_${treatKey}`;
        grouped[groupKey] = grouped[groupKey] || [];
        grouped[groupKey].push(geom);
      });
      for (const key in grouped) {
        const [projIDStr, treatIDStr] = key.split('_');
        const projID = parseInt(projIDStr, 10);
        const found = geometriesToProject.find((g) => {
          const rowProjId = g.treatment.ProjId ?? g.treatment.ProjectID;
          const rowTreatId = g.treatment.TreatId ?? g.treatment.TreatmentId ?? g.treatment.TreatmentID;
          return rowProjId === projID && String(rowTreatId) === treatIDStr;
        });
        if (!found) continue;
        const unioned = geometryEngine.union(grouped[key]) as __esri.Polyline;
        const t = found.treatment;
        const p = found.project;
        if (!p || !t) {
          console.warn(`Skipping Treatment ${t?.TreatmentId || t?.TreatmentID} due to missing data`);
          continue;
        }
        const atts = {
          OBJECTID: objectIdCounter++,
          ProjectID: p.ProjId ?? p.ProjectID,
          SystemID: p.SchemaId ?? p.SystemID,
          TreatmentID: t.TreatId ?? t.TreatmentId ?? t.TreatmentID,
          AssetType: t.TreatType ?? t.AssetType,
          Route: t.Rte ?? t.Route,
          SectionFrom: t.FromSection ?? t.SectionFrom,
          SectionTo: t.ToSection ?? t.SectionTo,
          BridgeID: t.BRIDGE_ID ?? t.BridgeID ?? '',
          TreatmentType: t.TreatType ?? t.TreatmentType,
          Treatment: t.Treatment,
          Year: t.Year,
          DirectCost: t.Cost ?? t.DirectCost ?? 0,
          DesignCost: t.DesignCost ?? 0,
          ROWCost: t.ROWCost ?? 0,
          UtilCost: t.UtilCost ?? 0,
          OtherCost: t.OtherCost ?? 0
        };
        //console.log('Adding graphic with attributes:', atts);
        graphics.push(
          new Graphic({
            geometry: unioned,
            attributes: atts,
            symbol: {
              type: 'simple-line',
              color: segmentTreatmentStyles[t.Treatment]?.color || [0, 0, 0, 1],
              width: 3
            }
          })
        );
      }
      const validGraphics = graphics.filter(
        (g) => g.geometry && g.attributes && g.attributes.ProjectID
      );
      if (!validGraphics.length) {
        console.error('No valid graphics to add to FeatureLayer!');
        return;
      }
      if (view.map.findLayerById(this.featureLayer.id)) {
        view.map.remove(this.featureLayer);
      }
      this.featureLayer.source = [];
      this.featureLayer
        .applyEdits({ addFeatures: validGraphics })
        .then((result) => {
          console.log(`Successfully added ${result.addFeatureResults.length} graphics.`);
        })
        .catch((error) => {
          console.error('Error applying edits:', error);
        });
      view.map.add(this.featureLayer);
      if (validGraphics.length > 0) {
        let fullExtent = validGraphics[0].geometry.extent.clone();
        validGraphics.forEach((g) => {
          fullExtent = fullExtent.union(g.geometry.extent);
        });
        const bufferFactor = 0.3;
        const expandedExtent = fullExtent.expand(1 + bufferFactor);
        view.goTo({ target: expandedExtent });
      }
    } catch (err) {
      console.error('Error loading data:', err);
    }
  }

  render() {
    return (
      <div style={{ height: '100%', width: '100%', overflow: 'auto' }}>
        {this.renderImportControls()}
        {this.props.useMapWidgetIds && this.props.useMapWidgetIds.length > 0 ? (
          <JimuMapViewComponent
            useMapWidgetId={this.props.useMapWidgetIds[0]}
            onActiveViewChange={this.activeViewChangeHandler}
          />
        ) : (
          <p>Please select a map.</p>
        )}
      </div>
    );
  }
}