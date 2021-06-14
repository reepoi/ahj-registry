import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
import FileSaver from "file-saver";
import createPersistedState from 'vuex-persistedstate';
import constants from "./constants";
import * as utils from "./utils.js"

/*
 * A Vuex store is a global state for the web application.
 * It has variables and methods that can be accessed from
 * all components and views.
 * 
 * Mutations, the methods of the store, are similar to creating Promises.
 * 
 * To modify a variable in the store, be sure to call the relevant mutation
 * or create a new one. New mutation methods take up to two arguments: state; custom arg
 * 
 * Access these store variables in elsewhere using 'this.$store.state.<variable_name>'
 * Call mutations with:
 *  - 'this.$store.commit("<mutation_name>");
 *  - 'this.$store.commit("<mutation_name>", <custom_arg>);'
 */

Vue.use(Vuex);

export default new Vuex.Store({
    plugins: [createPersistedState({
        paths: ['loginStatus'],
        storage: window.localStorage,
    })],
    state: {
        apiData: [],
        currentAHJ: null,
        cancelAPICallToken: null,
        apiLoading: true,
        apiError: false,
        showTable: false,
        selectedAHJ: null,
        editList: null,
        loginStatus: {
            Username: "",
            MaintainedAHJs: [],
            Photo: "",
            authToken: "",
            isSuperuser: false
        },
        currentUserInfo: null,
        searchedQuery: null,
        searchedGeoJSON: null,
        resultsDownloading: false,
        downloadCompletionPercent: 0
    },
    getters: {
        apiData: state => state.apiData,
        loggedIn: state => state.loginStatus.authToken !== "",
        authToken: state => state.loginStatus.authToken ? state.loginStatus.authToken : constants.TOKEN_AUTH
    },
    mutations: {
        callAPI(state, queryPayload) {
            state.apiLoading = true;
            if (!state.showTable) {
                state.showTable = true;
            }
            // If another axios request has been made; cancel it
            if (state.cancelAPICallToken !== null) {
                state.cancelAPICallToken("previous request cancelled");
            }
            let url = constants.API_ENDPOINT + "ahj-private/?";
            if (queryPayload) {
                state.searchedQuery = queryPayload;
            }
            if (queryPayload['Pagination']) {
                url += queryPayload['Pagination'];
            }
            if (queryPayload['callerID'] === 'searchpagefilter' && state.searchedGeoJSON) {
                queryPayload['FeatureCollection'] = state.searchedGeoJSON;
            }
            axios
                .post(url, queryPayload, {
                    headers: {
                      Authorization: `${this.getters.authToken}`,
                    },
                    cancelToken: new axios.CancelToken(function executor(c) {
                        state.cancelAPICallToken = c;
                    })
                })
                .then(response => {
                    state.apiData = response.data;
                    state.cancelAPICallToken = null;
                    state.apiLoading = false;
                    if (state.apiData.count > 0) {
                        state.selectedAHJ = state.apiData.results.ahjlist[0];
                    }
                })
                .catch((err) => {
                  // request was cancelled or some other error
                  if(err.message !== 'previous request cancelled'){
                    this.state.apiError = true;
                    this.state.apiLoading = false;
                  }
                });
        },
        setSelectedAHJ(state, ahj) {
            state.selectedAHJ = ahj;
        },
        setSearchGeoJSON(state, geojson) {
            state.searchedGeoJSON = geojson;
        },
        setShowTable(state, payload) {
            state.showTable = payload;
        },
        exportSearchResultsJSONCSV(state, fileType) {
          // Don't try to download if already downloading or no results yet
          if (state.resultsDownloading || state.selectedAHJ === null) {
            return;
          }
          state.resultsDownloading = true;
          let gatherAllObjects = function(url, searchPayload, ahjJSONObjs, offset) {
            if (url === null) {
              let filename = "results";
              let fileToExport = null;
              if (fileType === "application/json") {
                fileToExport = JSON.stringify(ahjJSONObjs, null, 2);
                filename += ".json";
              } else if (fileType === "text/csv") {
                fileToExport = utils.jsonToCSV(ahjJSONObjs);
                filename += ".csv";
              }
              FileSaver.saveAs(new Blob([fileToExport], {
                type: fileType
              }), filename);
              state.resultsDownloading = false;
              state.downloadCompletionPercent = 0;
            } else {
              axios
                .post(url, searchPayload,{
                  headers: {
                    Authorization: constants.TOKEN_AUTH_PUBLIC_API
                  }
                })
                .then(response => {
                  ahjJSONObjs = ahjJSONObjs.concat(response.data['AuthorityHavingJurisdictions']);
                  offset += 20; // the django rest framework pagination configuration
                  state.downloadCompletionPercent = (offset / response.data.count * 100).toFixed();
                  gatherAllObjects(response.data.next, searchPayload, ahjJSONObjs, offset);
                });
            }
          };
          let url = constants.API_ENDPOINT + "ahj/";
          let searchPayload = utils.value_to_ob_value_primitive(state.searchedQuery);
          if (state.searchedQuery.Address) {
              /* If an address was searched, the lat,lon coordinates are returned from callAPI.
               * Replace the address searched with a Location of the lat,lon.
               */
              delete searchPayload.Address;
              searchPayload['Location'] = state.apiData.results.Location;
          }
          if (state.searchedGeoJSON) {
            searchPayload['FeatureCollection'] = state.searchedGeoJSON;
          }
          gatherAllObjects(url, searchPayload, [], 0);
        },
        changeUserLoginStatus(state, payload) {
            state.loginStatus = payload;
            state.currentUserInfo = null;
        },
        changeCurrentUserInfo(state, payload) {
          state.currentUserInfo = payload;
        },
        getEdits(state,query){
          let url = constants.API_ENDPOINT + "edit/?" + query;
          axios
              .get(url, {
                  headers: {
                      Authorization: this.getters.authToken
                  },
                  cancelToken: new axios.CancelToken(function executor(c) {
                      state.cancelAPICallToken = c;
                  })
              })
              .then(response => {
                  state.editList = response.data;
                  state.cancelAPICallToken = null;
                  state.apiLoading = false;
              })
        },
        clearState(state){
                state.callData = [];
                state.leafletMap = null;
                state.leafletMarker = null;
                state.polygons = null;
                state.currPolyInd = null;
                state.apiLoading = true;
                state.mapViewCenter = [34.05, -118.24];
        }
    }
});
