<template>
    <div class="not-found-component-container">
    <b-row align-h="center" align-v="center" class="top-buffer">
        <b-col cols="11" md="8" lg="6" xl="4">
        <div class="shadow px-5 py-3 bg-white rounded" id="not-found-container">
            <h1 id="not-found-title">
                {{unknownType}} not found
            </h1>
            <div class="icon-container">
                <b-icon class="icon" icon="question" font-scale="7.5"></b-icon>
                <b-icon class="icon" icon="question" font-scale="7.5"></b-icon>
                <b-icon class="icon" icon="question" font-scale="7.5"></b-icon>
            </div>
        </div>
        </b-col>
    </b-row>
  </div>
</template>

<script>
export default {
    data() {
        return {
            unknownType: 'Page',
        }
    },
    mounted() {
        if (this.$route.params.unknownType) {
            this.unknownType = this.$route.params.unknownType;
        }
    },
}
</script>

<style scoped>
    .not-found-component-container {
        background-color: #f7f7f7;
    }

    #not-found-title {
        font-size: 3.2em;
        text-align: center;
    }

    .form-spacing {
        display: block;
        padding-bottom:.5rem;
    }

    .top-buffer { 
        margin-top:10%; 
    }

    .icon-container {
        margin-top: 1.5em;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .icon {
        animation-name: success;
        color: #7a7775;
        animation-duration: 1.8s;
        animation-iteration-count: 1;
        animation-timing-function: ease-out;
    }

    @keyframes success {
        0% {
            color: white;
            transform: rotate(0deg);
            opacity: 0;
        }
        90% {
            transform: rotate(370deg);
            opacity: 1;
        }
        100% {
            transform: rotate(360deg);
        }
    }

</style>