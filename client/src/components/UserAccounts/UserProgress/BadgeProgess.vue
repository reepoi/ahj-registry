<template>
    <div class="badge-progress">
        <h5>{{badgeName}}</h5>
        <div class="badge-progress-bar">
            <!-- Left badge -->
            <img class="stat-icon left-badge" :src="require('@/assets/' + badgeData['currBadge'] + '')">
            <!-- Progress bar and progress bar label -->
            <div class="progress-bar-container">
                <p class='progress-bar-text'>{{Math.abs(badgeData['max']-badgeData['score'])}} more {{actions}} before the next badge</p>
                <b-progress class="w-100" height="4vh" :max="adjustedMax">
                    <b-progress-bar :value="adjustedValue" :label-html="`<span class='progress-label'>${badgeData['score']}</span>`" variant="orange" striped animated></b-progress-bar>
                </b-progress>
            </div>
            <!-- Right badge -->
            <img class="stat-icon right-badge" :src="require('@/assets/' + badgeData['nextBadge'] + '')">
        </div>
        <p class='small-progress-bar-text'>{{Math.abs(badgeData['max']-badgeData['score'])}} more {{actions}} before the next badge</p>
    </div>
</template>

<script>
export default {
    // badgeData contains values: score, currBadge, nextBadge, and max.
    props: ['badgeName', 'badgeData'],
    computed:{
        // Returns what type of actions the user would need to do in order to fill up the progress bar.
        actions() {
            if (this.badgeName === 'Edits Accepted') return 'edits';
            else if (this.badgeName === 'Community Score') return 'points';
            else return 'api calls';
        },
        // Adjusted values make it so the progress bar does not start at 0 (completely empty)
        adjustedMax() {
            return parseInt(this.badgeData['max']) + this.badgeData['max']/10;
        },
        adjustedValue() {
            return parseInt(this.badgeData['score']) + this.badgeData['max']/10;
        }
    }
}
</script>

<style scoped>
h5 {
    font-size: 2rem;
    text-align: center;
}

p {
    margin-bottom: 0 !important;
}

.badge-progress {
    margin-bottom: 3em;
    display: flex;
    flex-direction: column;
}

.badge-progress-bar {
    display:flex;
    align-items: center;
    justify-content: space-between;
}

.progress-bar-container {
    flex: 3;
    min-width:15em;
    text-align: center;
}

p.progress-label {
    margin-bottom: 0 !important;
}

.small-progress-bar-text {
    display: none;
}

.progress-bar-text {
    margin: 0 auto! important;
    width: 90%;
}

.progress {
    font-size: 1.2rem !important;
    font-weight: bold;
    margin-bottom: 0 !important;
}

.bg-orange {
      background-color: #ff8c00 !important;
}

.stat-icon {
    flex:1;
    width: 10%;
    min-width: 6em;
}

.left-badge {
    transform: translateX(1em);
}

.right-badge {
    transform: translateX(-1em);
}

@media (max-width: 1000px){
    .progress-bar-container {
        min-width:5em;
    }
    .progress-bar-text {
        display: none;
    }
    .small-progress-bar-text {
        display: block;
        margin-top: 0.5em;
        text-align: center;
    }
}

@media (max-width: 800px){
    .badge-progress-bar {
        margin-bottom: 0.5em;
    }
    .badge-progress {
        margin-bottom: 5em;
    }
    h5 {
        font-size: 1.5rem;
        margin-bottom: 0.5em;
    }

    p {
        font-size: 0.8rem;
    }

    .progress {
        font-size: 0.75rem !important;
    }

    .stat-icon {
        width: 30%;
        min-width: 5em;
    }
}

</style>