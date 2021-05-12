<template>
    <div class="leaderboard-ranking-container">
        <h4>{{rankingTitle}}</h4>
        <hr>
        <div class="leaderboard-ranking">
            <!-- header row for the table (follows same structure as a relative-ranking-row)-->
            <relative-ranking-row rank="Rank"
            name="Username"
            score="Amount"
            isHeader="true"
            ></relative-ranking-row>
            <!-- Row component of a relative ranking table. Displays data about that specific user.-->
            <relative-ranking-row 
                v-for="(user, index) in rankings" 
                v-bind:key="user.Username" 
                v-bind:rank="rank + index"
                v-bind:name="user.Username"
                v-bind:score="userScore(user)"
            ></relative-ranking-row>
        </div>
    </div>
</template>

<script>
import RelativeRankingRow from "./RelativeRankingRow.vue";
export default {
    // rankings is the list of user objects that need to be displayed for this ranking type.
    props: ['rankingTitle', 'rankings', 'rank'],
    components: {
    "relative-ranking-row": RelativeRankingRow
  },
  computed:{
        username(){
            return this.$store.state.currentUserInfo.Username;
        }
    },
    methods: {
        // Grab the score this user has for this specific ranking type.
        userScore(user){
            if (this.rankingTitle == 'Submitted Edits') return user.SubmittedEdits;
            else if (this.rankingTitle == 'Accepted Edits') return user.AcceptedEdits;
            else return user.CommunityScore;
        }
    }
}
</script>

<style scoped>
h4 {
    text-align: center;
}

hr {
    width: 50%;
}

.leaderboard-ranking-container {
    flex:1;
}

.leaderboard-ranking {
    height: 80%;
    margin: auto;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 0em 2em;
}

</style>