<template>
    <!-- Relative ranking rows contian a rank, a user photo, a username, and a score --> 
    <div class="ranking-row" :class="{'current-user-row' : isLoggedInUser}">
        <p class="ranking-row-rank">{{rank}}</p>
        <template v-if="!isHeader">
            <!-- Show default photo if the user is not logged in. -->
            <img v-if='!isLoggedInUser' class='ranking-row-image' src="../../../assets/images/profile-image-default.jpeg"/>
            <img v-else class='ranking-row-image current-user-image' :src="$store.state.currentUserInfo.Photo"/>
        </template>
        <p class="ranking-row-username">{{name}}</p>
        <p class="ranking-row-score">{{score}}</p>
    </div>
</template>

<script>
export default {
    props: ['name', 'score', 'rank', 'isHeader'],
    computed: {
        isLoggedInUser() {
            return this.name == this.$store.state.currentUserInfo.Username;
        }
    }
}
</script>

<style scoped>
p {
    padding: 0;
    margin: 0;
}
.ranking-row {
    display: grid;
    justify-content: center;
    text-align: center;
    place-items: center;
    grid-auto-columns: 10% 20% 55% 15%;
}

.current-user-row {
    background-color:#f0fdff;
    padding: 1em 0em;
}

.current-user-row > p {
    font-weight: 900;
    font-size: 1.15rem;
}

.ranking-row-rank {
    grid-column: 1;
}

.ranking-row-image {
    max-width: 2em;
    max-height: 2em;
    border-radius: 2em;
    grid-column: 2;
    margin-left: 0.5em;
}

.current-user-image {
    max-width: 3em;
    max-height: 3em;
    border-radius: 3em;
}

.ranking-row-username {
    grid-column: 3;
}

.ranking-row-score {
    grid-column: 4;
}

</style>