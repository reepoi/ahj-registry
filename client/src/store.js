import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
import constants from "./constants.js";
import FileSaver from "file-saver";
import * as utils from "./utils";

Vue.use(Vuex);

// TODO: Refactor API calls so hasNext and hasPrevious are set via a function to reduce repeated code. will need to move some mutations to actions
// Add query string to set offsets against for pagination
export default new Vuex.Store({
  state: {
    apiData: [],
    apiURL: constants.API_ENDPOINT,
    apiURLAddon: "",
    apiLoading: true,
    cancelAPICallToken: null,
    hasNext: false,
    hasPrevious: false,
    currentPage: 1,
    ahjCount: "",
    dataReady: false,
    perPage: 20,
    queryString: "",
    loginStatus: {
      status: "",
      isSuper: false,
      isStaff: false,
      authToken: ""
    },
    showLoginModal: false,
    selectedAHJ: null,
    resultsDownloading: false,
    downloadCompletion: 0,
    showTable: false
  },
  getters: {
    apiData: state => state.apiData
  },
  mutations: {
    callAPI(state, payload) {
      if (!state.showTable) {
        state.showTable = true;
      }
      // If another axios request has been made; cancel it
      if (state.cancelAPICallToken !== null) {
        state.cancelAPICallToken("previous request cancelled");
      }
      let url = state.apiURL + state.apiURLAddon + "?";
      if (payload) {
        url += payload;
      }
      axios
        .get(url, {
          headers: {
            Authorization: constants.TOKEN_AUTH
          },
          cancelToken: new axios.CancelToken(function executor(c) {
            state.cancelAPICallToken = c;
          })
        })
        .then(response => {
          state.apiData = response.data;
          state.ahjCount = response.data.count;
          state.hasNext = Boolean(response.data.next);
          state.hasPrevious = Boolean(response.data.previous);
          state.cancelAPICallToken = null;
          state.apiLoading = false;
          if (state.apiData.results.ahjlist.length > 0) {
            state.selectedAHJ = state.apiData.results.ahjlist[0];
          }
          state.dataReady = true;
        })
        .catch((/*err*/) => {
          // request was cancelled or some other error
        });
    },
    callHistoryAPI(state, payload) {
      // If another axios request has been made; cancel it
      if (state.cancelAPICallToken !== null) {
        state.cancelAPICallToken("previous request cancelled");
      }
      let url = state.apiURL + state.apiURLAddon + "?";
      if (payload) {
        url += payload;
      }
      axios
        .get(url, {
          headers: {
            Authorization: constants.TOKEN_AUTH
          },
          cancelToken: new axios.CancelToken(function executor(c) {
            state.cancelAPICallToken = c;
          })
        })
        .then(response => {
          state.apiData = response.data;
          state.ahjCount = response.data.count;
          state.hasNext = Boolean(response.data.next);
          state.hasPrevious = Boolean(response.data.previous);
          state.cancelAPICallToken = null;
          state.apiLoading = false;
        })
        .catch((/*err*/) => {
          // request was cancelled or some other error
        });
    },
    deleteAPIData(state) {
      state.apiData = [];
      state.ahjCount = "";
    },
    modifyApiDataAHJList(state, payload) {
      Vue.set(state.apiData.results.ahjlist, payload.index, payload.newahj);
    },
    setShowLoginModal(state, payload) {
      state.showLoginModal = payload;
    },
    setAPILoading(state, payload) {
      state.apiLoading = payload;
    },
    toggleDataReady(state) {
      state.dataReady = false;
    },
    setQueryString(state, payload) {
      state.queryString = payload;
    },
    updateCurrentPage(state, value) {
      state.currentPage = value;
    },
    setApiUrlAddon(state, value) {
      state.apiURLAddon = value;
    },
    exportResults(state, fileType) {
      // Don't try to download if no results yet
      if (state.ahjCount === 0) {
        state.resultsDownloading = false;
        return;
      }
      state.resultsDownloading = true;
      let gatherAllObjects = function(url, ahjJSONObjs, offset) {
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
          state.resultsDownloading = false;
          state.downloadCompletion = 0;
          FileSaver.saveAs(new Blob([fileToExport], {
            type: fileType
          }), filename);
        } else {
          axios
            .get(url, {
              headers: {
                Authorization: constants.TOKEN_AUTH
              }
            })
            .then(response => {
              ahjJSONObjs = ahjJSONObjs.concat(response.data.results);
              offset += 20; // the django rest framework pagination configuration
              state.downloadCompletion = (offset / state.ahjCount * 100).toFixed();
              gatherAllObjects(response.data.next, ahjJSONObjs, offset);
            });
        }
      };
      let url = state.apiURL + "ahj/";
      if (state.queryString) {
        url += "?" + state.queryString;
      }
      gatherAllObjects(url, [], 0);
    },
    changeUserLoginStatus(state, payload) {
      state.loginStatus = payload;
    },
    setSelectedAHJ(state, ahj) {
      state.selectedAHJ = ahj;
    },
    setShowTable(state, payload) {
      state.showTable = payload;
    }
  }
});
