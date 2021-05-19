<template>
  <div id="app">
    <Navbar id="navbar" @event-open-modal="openChatModal()"/>
    <router-view @event-open-modal="openChatModal()" id="router-v" />
    <!-- Modal to show chal using vue-advanced-chat -->
    <b-modal size="xl" v-model="showChat" :hide-footer="true">
      <!-- fields needed for vue-advanced-chat -->
      <chat-window
          :current-user-id="currentUserId"
          :rooms="$store.state.rooms"
          :messages="messages"
          :messages-loaded="isLoaded"
          :rooms-loaded="true"
          @fetch-messages="setUpMessaging"
          @send-message="sendMessage"
          :show-audio="false"
          :show-files="false"
          :show-add-room="false"
          :message-actions="[]"
          :show-reaction-emojis="false"
      />
    </b-modal>
  </div>
</template>

<script>
import Navbar from "./components/Navbar.vue";
import PubNub from "pubnub";
import ChatWindow from 'vue-advanced-chat';
import axios from "axios";
import 'vue-advanced-chat/dist/vue-advanced-chat.css';
import constants from "./constants.js";
import * as utils from "./utils.js"

export default {
  components: {
    Navbar,
    ChatWindow
  },
  data() {
    return {
      currentUserId: '',
      rooms: [],
      messages: [],
      currentRoom: null,
      isLoaded: false,
      currMessageIndex: 0,
      showChat: false,
      totUnread: 0
    }
  },
  mounted() {
    if (this.$store.getters.loggedIn) {
      this.$store.dispatch('getUserInfo')
    }
  },
  methods: {
    initializeChat(userInfo) {
      if(this.$store.state.pubnub){
        //if already subcribe, unsubcribe from all and reset pubnub object in store
        this.$store.state.pubnub.unsubscribeAll();
        this.$store.state.pubnub.removeAllListeners();
        this.$store.state.pubnub = null;
      }
      if(userInfo.Username){
        //if user is logged in, connect to pubnub API
        this.$store.state.pubnub = new PubNub({
          publishKey: "pub-c-21263604-71e0-42f2-baaf-4f99b69164ed",
          subscribeKey: "sub-c-1da21552-8d04-11eb-bfcb-9a3fb4a80a34",
          uuid: userInfo.Username
        });
        this.$store.commit("setRooms");
        //add a message listener
        this.$store.state.pubnub.addListener({message: M => {
            if(M.channel === "control" && M.message.user === userInfo.Username){
              //if request for this user to subscribe to chat rooms, add that room to this user saved rooms
              var chats = this.$store.state.currentUserInfo.ChatRooms;
              chats.push(M.message.data);
              this.$store.state.currentUserInfo.ChatRooms = chats;
              //reset chatrooms
              this.$store.commit("setRooms");
            }
            else{
              if (M.channel === this.currentRoom) {
                //if messages comes through the current room, add to messages array
                this.messages = [...this.messages, {
                  _id: this.currMessageIndex, content: M.message.text, senderId: M.publisher, username: M.publisher,
                  saved: true, distributed: false, seen: true, new: false
                }]
                this.currMessageIndex += 1;
                //set timestamp to message timestamp so backend knows this message was read
                axios.post(constants.API_ENDPOINT + 'adjust-timestamp/',{ChannelID : M.channel, Token: M.timetoken},{headers: {Authorization: this.$store.getters.authToken}});
                for(i = 0; i < userInfo.ChatRooms.length; i++){
                  //increase last read token time in current chatroom
                  if(userInfo.ChatRooms[i].ChannelID === this.currentRoom){
                    userInfo.ChatRooms[i].LastReadToken = M.timetoken;
                  }
                }
                //set users chatroom
                this.$store.state.currentUserInfo.ChatRooms = userInfo.ChatRooms;
              }
              for(var i = 0; i < this.$store.state.rooms.length; i++){
                var room = this.$store.state.rooms[i]
                //change message's room's last message object
                if(room.roomId === M.channel){
                  var msg = utils.getMessageObject(M);
                  room.lastMessage = msg;
                  if(this.currentRoom !== room.roomId){
                    //if we're not in this room, increase its unread count
                    room.unreadCount += 1;
                    //this.totUnread += 1;
                  }
                  this.$store.state.rooms = [...this.$store.state.rooms];
                  break;
                }
              }
            }
          }});
      }
    },
    setUpMessaging(roomAndOption) {
      if(roomAndOption.options && roomAndOption.options.reset) {
        //if we opened a new room messages arent loaded and set current room ID
        this.isLoaded = false;
        this.currMessageIndex = 0;
        this.currentRoom = roomAndOption.room.roomId;
        this.messages = [];
        //fetch last 25 messages
        this.$store.state.pubnub.fetchMessages({
              channels: [roomAndOption.room.roomId],
              count: 25
            },
            (status, response) => {
              if(!response || !response.channels[roomAndOption.room.roomId]){
                //if no messages return
                this.messages = [];
                this.isLoaded = true;
                return;
              }
              //create message objects and add to array
              let messages = response.channels[roomAndOption.room.roomId].map(c => {
                let vueChatMessage = utils.getMessageObject(c);
                vueChatMessage['_id'] = this.currMessageIndex;
                this.currMessageIndex += 1;
                return vueChatMessage
              });
              this.messages = messages;
              if(this.messages.length < 25){
                //if we pull fewer than 25 messages, then all messages in this channel have been loaded
                this.isLoaded = true;
              }
              //set timestamp of this room to last read message
              axios.post(constants.API_ENDPOINT + 'adjust-timestamp/',{ChannelID : this.currentRoom,
                Token: this.messages[this.messages.length - 1].timetoken},{headers: {Authorization: this.$store.getters.authToken}}).then(() => {
                if(this.messages.length > 0){
                  let chatrooms = this.$store.state.currentUserInfo.ChatRooms;
                  //find chat room and reset last read tiemtoken for that room
                  for(i = 0; i < chatrooms.length; i++){
                    if(chatrooms[i].ChannelID === this.currentRoom){
                      chatrooms[i].LastReadToken = this.messages[this.messages.length - 1].timetoken;
                    }
                  }
                  this.$store.state.currentUserInfo.ChatRooms = chatrooms;
                }
                //set unread count for this room to 0
                let rooms = this.$store.state.rooms;
                for(var i = 0; i < this.$store.state.rooms.length; i++){
                  if(this.currentRoom === this.$store.state.rooms[i].roomId){
                    this.totUnread -= this.$store.state.rooms[i].unreadCount;
                    rooms[i].unreadCount = 0;
                    this.$store.state.rooms = rooms;
                  }
                }
              });
            });
      }
      //fetch more messages from same chat room
      else{
        //fetch next 25 messages
        this.$store.state.pubnub.fetchMessages({
              channels: [roomAndOption.room.roomId],
              start: this.messages[0].timetoken,
              count: 25
            },
            (status, response) => {
              status;
              if(response === null){
                //if no messages, all have been loaded
                this.isLoaded = true;
                return null;
              }
              //create message objects and add to array
              let messages = response.channels[roomAndOption.room.roomId].map(c => {
                let vueChatMessage = utils.getMessageObject(c);
                vueChatMessage.seen = true;
                vueChatMessage['_id'] = this.currMessageIndex;
                this.currMessageIndex += 1;
                return vueChatMessage;
              });
              if(messages.length < 25){
                //if we;ve received less than 25 messages, then all messages are loaded
                this.isLoaded = true;
              }
              //add newly loaded messages to messages array
              this.messages = [...messages,...this.messages];
            });
      }
    },
    sendMessage(e) {
      let roomId = e.roomId;
      let content = e.content;
      //publish message from current room
      this.$store.state.pubnub.publish({
        channel: roomId,
        message: {
          text: content
        }
      });
    },
    //open the chat modal
    openChatModal() {
      this.$store.commit("setRooms");
      this.showChat = true;
      //this.currentRoom = "";
    },
  },
  watch: {
    //if we add a room, change total unread token
   '$store.state.rooms': function () {
      for (var i = 0; i < this.$store.state.rooms.length; i++) {
        this.totUnread += this.$store.state.rooms[i].unreadCount;
      }
    },
    //if user info gets reinitialized (user logs in or out)
    '$store.state.currentUserInfo': function(userInfo) {
      if (userInfo) {
        //if user logs in, initialize chat
        this.currentUserId = userInfo.Username;
        this.initializeChat(userInfo);
      } else {
        //user logs out, reset pubnub object to null and remove listeners
        this.$store.state.pubnub.unsubscribeAll();
        this.$store.state.pubnub.removeAllListeners();
        this.$store.state.pubnub = null;
      }
    },
    showChat: function(){
      //reset current room when user closes chat
      if(!this.showChat){
        this.currentRoom = "";
      }
    }
  }
};
</script>

<style>
#app {
  font-family: "Roboto Condensed";

  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  background-color: white;
  display: grid;
  grid-template-rows: 4.25em auto;
  height: 100vh;
}

#navbar {
  grid-row: 1 / 2;
}
</style>
