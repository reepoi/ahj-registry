<template>
    <div id="commentCard">
        <div>
             <img v-if="this.Comment === null || this.Comment.User.Photo === null" class='pfp' src='../../../src/assets/images/profile-image-default.jpeg'/>
             <img v-else v-bind:src="Comment.User.Photo" class='pfp'/>
        </div>
        <div class="info-text">
            <div class="username">
                <!-- Comment username and date -->
                <h3 class="text">{{this.Comment.User.Username}}</h3>
                <h3 class="text">{{this.Date}}</h3>
            </div> 
            <span style="margin-top: 5px; margin-bottom: 5px;white-space: normal; word-wrap: anywhere;" class="text-box">{{`${this.Comment.CommentText.Value}`}}</span>
            <div v-if="!Reply">
                <!-- reply to a comment only if this comment is not a reply -->
            <b-button v-on:click="showReply()" v-if="$store.getters.authToken !== ''" style="width:100px;margin-left:5px;" pill class="mr-2" size="sm">Reply</b-button>
            <form ref="reply" v-if="$store.getters.authToken !== ''" @submit.prevent="submitComment()" style="margin-bottom:15px;" class="hide">
                    <textarea v-model="commentInput" placeholder="Type a Comment..." type="text" class="input-comment"> </textarea>
                    <b-button class="mr-2" @submit.prevent="submitComment()" type="submit">Submit Reply</b-button>
            </form>
            </div>
            <!-- Show replies -->
            <comment-card @count="count" style="margin-top:25px;" v-for="comment in this.Comment.Replies" v-bind:key="comment.CommentID.Value" v-bind:Comment="comment" v-bind:Reply="true">
            </comment-card>
        </div>
    </div>
</template>

<script>
import moment from "moment";
import constants from '../../constants.js';
import axios from "axios";

export default {
    name: 'comment-card',
    props: {
        Comment: {
            type: Object
        },
        Reply: {
            type: Boolean
        }
    },
    data() {
        return {
            Date: "",
            commentInput: ""
        }
    },
    mounted(){
        //this.$store.commit('changeUserLoginStatus', JSON.parse(window.localStorage.vuex).loginStatus);
        //Convert date ton readable format
        this.Date = moment(this.Comment.Date.Value).format('MM/DD/YYYY hh:mm A');
        //send number of replies to parent object
        this.$emit('count',this.Comment.Replies.length);
    },
    methods: {
        showReply(){
            //toggle show reply div
            this.$refs.reply.classList.toggle('show');
            this.$refs.reply.classList.toggle('hide');
        },
        submitComment(){
            //check if comment is empty
            if(this.commentInput == ""){
                alert("Comment Cannot Be Empty");
                return;
            }
            //submit the comment
            let url = constants.API_ENDPOINT + 'ahj/comment/submit/';
            let data = { CommentText: this.commentInput, AHJPK: null, ReplyingTo: this.Comment.CommentID.Value };
            axios
                .post(url, data, {
                    headers: {
                        Authorization: this.$store.getters.authToken
                    }
                })
                .then(response => {
                    this.$refs.reply.classList.toggle('show');
                    this.$refs.reply.classList.toggle('hide');
                    this.Comment.Replies = [response.data, ...this.Comment.Replies];
                    response.data = "";
                    this.commentInput = "";
                    this.$emit('count', 1);
                })
        },
        count(num){
            //event handler for count of replies
            this.$emit('count', num);
        }
    }
}
</script>

<style scoped>
div,h3{
  font-family: "Roboto Condensed";
  text-align: center;
  color: #4b4e52;
  margin-bottom: 0px;
}
.info-text{
    display: flex;
    flex-wrap: wrap;
    flex-grow: 200;
    flex-direction: column;
    width: calc(100% - 110px);
    margin-bottom: 5px;
}
.username{
    position: relative;
    display: flex;
    justify-content: space-between;
    color: lightgrey;
    font-size: 15px;
    padding-top: 5px;
    border-bottom: 1px solid gray;
    width: 98%;
    left: 1%;
    max-height: 50px;
}
.text-box{
    position: relative;
    font-size: 15px;
    float: right;
    text-align: left;
    width: 98%;
    left: 1%;

    min-height: 60px;
}
.text{
    font-size: 15px;
    font-family: "Roboto Condensed";
  text-align: center;
  color: #4b4e52;
  margin-bottom: 0px;
}
#commentCard{
    border-radius: 5px;
    background-color: lightgrey;
    display: flex;
}
.pfp{
    width: 95px;
    height: 95px;
    border-radius: 100px;
    padding: 2.5px;
}
.input-comment{
    width: 98%;
    border: 0px;
    border-bottom: 1px solid gray;
    margin-bottom: 5px;
    margin-top: 20px;
    margin-right: 5px;
}
.hide{
    display: none;
}
.show{
    display: block;
}
</style>