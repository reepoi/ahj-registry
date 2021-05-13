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

    // Chat related fields
    pubnub: null, // An instance of the PubNub chat management service
    rooms: [] // The current chat rooms a user is participating in
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

                    // select first ahj in results as focus if results were returned
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

            // function to repeatedly call api with user's search, iterating through each page of results
            let gatherAllObjects = function(url, searchPayload, ahjJSONObjs, offset) {
                if (url === null) {
                    let filename = "results";
                    let fileToExport = null;

                    // prepare to download json
                    if (fileType === "application/json") {
                        fileToExport = JSON.stringify(ahjJSONObjs, null, 2);
                        filename += ".json";
                    } else if (fileType === "text/csv") { // prepare to download csv
                        fileToExport = utils.jsonToCSV(ahjJSONObjs);
                        filename += ".csv";
                    }

                    // save the file
                    FileSaver.saveAs(new Blob([fileToExport], {
                        type: fileType
                    }), filename);
                    state.resultsDownloading = false;
                    state.downloadCompletionPercent = 0;
                } else {
                    axios
                        .post(url, searchPayload,{
                            headers: {
                                Authorization: `Token ${constants.TOKEN_AUTH_PUBLIC_API}`
                            }
                        })
                        .then(response => {
                            ahjJSONObjs = ahjJSONObjs.concat(response.data.results);
                            offset += 20; // the django rest framework pagination configuration
                            state.downloadCompletionPercent = (offset / response.data.count * 100).toFixed();
                            gatherAllObjects(response.data.next, searchPayload, ahjJSONObjs, offset);
                        });
                }
            };
            let url = constants.API_ENDPOINT + "ahj/"; // calling public api endpoint to not include extra info in download
            let searchPayload = state.searchedQuery;

            // include searched region when downloading resutls
            if (state.searchedGeoJSON) {
                searchPayload['FeatureCollection'] = state.searchedGeoJSON;
            }

            // begin the iterative api calls
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
        setRooms(state){ // add chat rooms for user, new or saved
            state.pubnub.unsubscribeAll();
            state.pubnub.subscribe({channels: [ "control" ],withPresence: true});
            for(let i = 0; i < state.currentUserInfo.ChatRooms.length; i++){
                state.pubnub.subscribe({channels: [ state.currentUserInfo.ChatRooms[i].ChannelID ]})
            }
            let channelsWithTimes = [];
            if(state.currentUserInfo.ChatRooms.length === 0){
                return;
            }

            // get number of unread messages in the chat
            state.pubnub.messageCounts({
                channels: state.currentUserInfo.ChatRooms.map(c => c.ChannelID),
                channelTimetokens: state.currentUserInfo.ChatRooms.map(c => {return c.LastReadToken}) // TODO: set to real value
            }).then((response) => {
                channelsWithTimes = state.currentUserInfo.ChatRooms.map(c => {
                    let result = JSON.parse(JSON.stringify(c));
                    result['NumberUnread'] = response.channels[result.ChannelID];
                    return result;
                });

                // get the last sent message in the chat, if it exits
                state.pubnub.fetchMessages({
                        channels: state.currentUserInfo.ChatRooms.map(c => c.ChannelID),
                        count: 1
                    },
                    (status, response) => {
                        if(response === null){
                            let rooms = channelsWithTimes.map(c => utils.getRoomObject(c,state.currentUserInfo.Username));
                            state.rooms = rooms;
                            return;
                        }
                        for (let c of channelsWithTimes) {
                            if(response.channels[c.ChannelID]){
                                c['lastMessage'] = response.channels[c.ChannelID][0];
                            }
                        }
                        let rooms = channelsWithTimes.map(c => utils.getRoomObject(c,state.currentUserInfo.Username));
                        state.rooms = rooms;
                    });
            }).catch(() => {
                    // handle error
                }
            );
        },
    },
    actions: {
        async getUserInfo({state, getters, dispatch, commit}){ // get currently logged in user's info by their webpage auth token
            let query = constants.API_ENDPOINT + "user/active/" + state.authToken + "/";
            await axios.get(query, {
                headers: {
                    Authorization: getters.authToken
                }
            })
                .then(async (response) => {
                    let userInfo = response.data;
                    userInfo.Photo = await dispatch('convertBinaryToPhoto', userInfo.Photo);
                    commit('changeCurrentUserInfo', userInfo);
                });
        },
        convertBinaryToPhoto(context, binaryString) { // setup for displaying user's profile picture
            var binary = atob(binaryString.replace(/\s/g, ''));
            var len = binary.length;
            var buffer = new ArrayBuffer(len);
            var view = new Uint8Array(buffer);
            for (var i = 0; i < len; i++) {
                view[i] = binary.charCodeAt(i);
            }
            var blob = new Blob( [view], { type: "image/jpeg" });
            let objURL = URL.createObjectURL(blob);
            return objURL;
        },
    },
});
