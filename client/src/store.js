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
import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
import FileSaver from "file-saver";
import createPersistedState from 'vuex-persistedstate';
import constants from "./constants";
import * as utils from "./utils.js"


Vue.use(Vuex);

export default new Vuex.Store({
  plugins: [createPersistedState({ // Keeps logged in users logged in over page reloads
    paths: ['authToken'],
    storage: window.localStorage,
})],
state: {
    apiData: [], // stores results of ahj search page
    currentAHJ: null, // Current AHJ in focus on map and AHJ table
    cancelAPICallToken: null, // Field to call .cancel() on to cancel an axios api request
    apiLoading: true,
    apiError: false,
    apiErrorStatusCode: null,
    showTable: false, // shows the search results table
    selectedAHJ: null, // Current AHJ in focus on map and AHJ table
    editList: null,
    authToken: "", // auth token of the current logged in user; used to call apis when user is logged in
    currentUserInfo: null, // info of user currently logged in (not saved after page reload)
    searchedQuery: null, // query entered on ahj search page
    searchedGeoJSON: null, // query of region drawn on map

    // Controls interface for downloading results
    resultsDownloading: false, // Enables or disables download results button
    downloadCompletionPercent: 0, // Updates downloading progress of results
},
    getters: {
        apiData: state => state.apiData,
        loggedIn: state => state.authToken !== "",
        authToken: state => state.authToken ? "Token " + state.authToken : "Token " + constants.TOKEN_AUTH, // gets webpage's webpage api token or currently logged in api token
        currentUserInfo: state => state.currentUserInfo,
    },
    mutations: {
        callAPI(state, queryPayload) {
            state.apiLoading = true;
            this.state.apiErrorStatusCode = null;
            if (!state.showTable) {
                state.showTable = true;
            }
            // If another axios request has been made; cancel it
            if (state.cancelAPICallToken !== null) {
                state.cancelAPICallToken("previous request cancelled");
            }
            let url = constants.API_ENDPOINT + "ahj-private/?";

            // save query for other components to modify and perform current search later
            if (queryPayload) {
                state.searchedQuery = queryPayload;
            }

            // track what page of results is being searched
            if (queryPayload['Pagination']) {
                url += queryPayload['Pagination'];
            }

            // if ahj search api was called by AHJSearchFilter, check if there was a regioin searched too
            if (queryPayload['callerID'] === 'searchpagefilter' && state.searchedGeoJSON) {
                queryPayload['FeatureCollection'] = state.searchedGeoJSON;
            }
            let headers = {};
            if (this.getters.loggedIn) {
                headers.Authorization = this.getters.authToken;
            }
            axios
                .post(url, queryPayload, {
                    headers: headers,
                    cancelToken: new axios.CancelToken(function executor(c) {
                        state.cancelAPICallToken = c;
                    })
                })
                .then(response => {
                    state.apiData = response.data;
                    state.cancelAPICallToken = null;
                    state.apiLoading = false;

                    // select first ahj in results as focus if results were returned
                    if (state.apiData.count > 0) {
                        state.selectedAHJ = state.apiData.results.ahjlist[0];
                    }
                })
                .catch((err) => {
                    if (err.response){
                        this.state.apiErrorStatusCode = err.response.status;
                    }
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
        changeAuthToken(state, authToken) {
            state.authToken = authToken;
        },
        changeCurrentUserInfo(state, payload) {
            state.currentUserInfo = payload;
        },
        getEdits(state,query){
            let url = constants.API_ENDPOINT + "edit/?" + query;
            axios
                .get(url, {
                    headers: {
                        Authorization: `${this.getters.authToken}`
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
        clearState(state){ // reset fields in the store
            state.callData = [];
            state.leafletMap = null;
            state.leafletMarker = null;
            state.polygons = null;
            state.currPolyInd = null;
            state.apiLoading = true;
            state.mapViewCenter = [34.05, -118.24];
        },
    },
    actions: {
        async getUserInfo({getters, commit}){ // get currently logged in user's info by their webpage auth token
            let query = constants.API_ENDPOINT + "user/active/";
            await axios.get(query, {
                headers: {
                    Authorization: getters.authToken
                }
            })
                .then(async (response) => {
                    let userInfo = response.data;
                    commit('changeCurrentUserInfo', userInfo);
                });
        },
    },
});
