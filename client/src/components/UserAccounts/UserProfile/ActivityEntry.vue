<template>
    <div class="activity-container">
        <div class="activity-header">
            <img class="user__image" src="../../../assets/images/profile-image-default.jpeg">
            <span class="name">{{FullName}}</span>
            <b-icon icon="circle-fill" class="circle-icon"></b-icon> 
            <span class="date">{{this.dateText}}</span>
        </div>
        <div class="activity-body">
            <!-- Upvote/ downvote section. At the moment, div serves as indentation. -->
            <div class="activity-score">
                <!-- <b-icon class="h4 mb-2 arrow-icon" icon="arrow-up"></b-icon>
                <span class="score">{{this.score}}</span>
                <b-icon class="h4 mb-2 arrow-icon" icon="arrow-down"></b-icon> -->
            </div>
            <!-- displays either an edit or a comment depending on entry type-->
            <div class="activity-content" v-if="ActivityType === 'Edit'">
                <edit v-bind:ActivityData="this.ActivityData"></edit>
            </div>
            <div class="activity-content" v-else>
                <comment v-bind:ActivityData="this.ActivityData"></comment>
            </div>
        </div>
    </div>
</template>
<script>
import Edit from "./Edit.vue";
import Comment from "./Comment.vue";
export default {
    props: ['UserData', 'ActivityType', 'ActivityData', 'Photo'],
    computed: {
        FullName(){
            return `${this.$props.UserData.ContactID.FirstName.Value} ${this.$props.UserData.ContactID.LastName.Value}`;
        },
    },
    data() {
        return {
            // display the date differently depending on if this is an edit entry or a comment entry.
            dateText: this.$props.ActivityType === 'Edit' ? `Submitted on: ${this.$props.ActivityData.DateRequested}` : this.$props.ActivityData.Date.Value.substring(0,10),
            score: 0,
            UserPhoto: ""
        }
    },
    components: {
    "edit": Edit,
    "comment": Comment
  },
  methods: {
      UpdateScore(value){
          this.score += value;
      }
  },
}
</script>

<style scoped>
.activity-container {
    width: 100%;
    margin: 20px 0px;
    border-bottom: lightgray 1px solid;
}
.activity-header {
    display: flex;
    margin-bottom: 1em;
    align-items: center;
}
.activity-header img {
    margin-left: 0.8em;
    margin-right: 1.3em;
}
.activity-body {
    display: flex;
}
.activity-score {
    flex: 1;
    justify-content: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-bottom: 2em;
}
.activity-content {
    flex: 13;
}
.activity-header-info {
    display: flex;
    align-items: center;
}

.user__image {
    border-radius: 50px;
    border: 1.5px solid lightgray;
    height: 50px;
    width: 50px;
    object-fit: cover;
}
.score {
    font-size: 1.3em;
}
.arrow-icon {
    margin: 0 !important;
    cursor: pointer;
}
.name {
    font-size: 1.3em;
    vertical-align: center;
    margin-right: 0.5em;
}
.date {
    vertical-align: center;
}
.circle-icon {
    height: 0.4em;
    width: 0.4em;
    margin-right: 0.5em;
}
@media (max-width: 1000px){
    .activity-header-info {
        flex-direction: column;
        align-items: flex-start;
    }
    .circle-icon {
        display: none !important;
    }
    .activity-score {
        margin-right: 1em;
    }
}

@media (max-width: 600px){
    .activity-header img {
        margin-left: 0;
    }
}
</style>