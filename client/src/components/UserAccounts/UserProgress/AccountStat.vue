<template>
    <div class="account-stat">
        <!-- Account stat icon and corresponding number -->
        <div class="account-stat-header">
            <img class="stat-icon" :src="require('@/assets/' + icon + '')">
        </div>
        <hr>
        <!-- account stat section with the name of this type of stat. Optionally has an info-tooltip. -->
        <div class="account-stat-name-section" v-if="statName === 'Community Score'">
            <h4>{{statName}}</h4>
            <b-icon icon="info-circle-fill" scale="1" variant="info" id="info-tooltip-target"></b-icon>
            <b-tooltip target="info-tooltip-target" triggers="click hover" placement="right" variant="light">
                Submitting edits, making comments, and voting on existing edits
                all increase your community score. 
            </b-tooltip>
        </div>
        <div v-else>
            <h4>{{statName}}</h4>
        </div>
        <p class="stat-num">{{stat}}</p>
    </div>
</template>

<script>
export default {
    props: ['icon', 'stat', 'statName'],
}
</script>

<style scoped>
p {
    padding: 0;
    margin: 0;
}
hr {
    width: 70%;
    height: 2px;
    background-color: #8c8b8b;
    border: 0;
}
.account-stat {
    width: 22%;
    min-width: 10em;
    display: flex;
    flex-direction: column;
    text-align: center;
}

.account-stat-header{
    display: flex;
    justify-content: center;
    align-items: center;
}

.account-stat-name-section {
    display: flex;
    justify-content: space-evenly;
}

.stat-icon {
    max-height: 6em;
}

.stat-num {
    flex: 1;
    font-size: 3vw;
    font-weight: 500;
}

@media (min-width: 2000px){
    .stat-icon {
        max-height: 8em;
    }
    h4 {
        font-size: 1.8rem;
    }
}

@media (max-width: 1500px){
    h4 {
        font-size: 1.4vw;
    }
}

@media (max-width: 1000px){
    h4 {
        font-size: 1rem;
    }
    .stat-num {
        flex: 1;
        font-size: 1.5rem;
        font-weight: 500;
    }
}

</style>