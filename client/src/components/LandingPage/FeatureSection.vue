<template>
    <div class="feature-section-container">
        <div class="image-section" v-if="pictureSide === 'left'" data-aos="fade-right" data-aos-duration="1000">
            <img :src="require('@/assets/' + imgSrc + '')">
        </div>

        <div class="info-section" :class="(pictureSide === 'left') ? 'info-section-right' : 'info-section-left'" v-bind:data-aos="isLeft" data-aos-duration="1000">
            <h2>{{headerText}}</h2>
            <h4>{{paragraphText}}</h4>
            <b-button @click="ChangePage" class="info-section-button" variant="primary" v-if="buttonText">{{buttonText}}</b-button>
        </div>

        <div class="image-section" v-if="pictureSide === 'right'" data-aos="fade-left" data-aos-duration="1000">
            <img class="image" :src="require('@/assets/' + imgSrc + '')">
        </div>

    </div>
</template>

<script>
export default {
    props: ['headerText', 'paragraphText', 'buttonText', 'buttonPageLink', 'pictureSide', 'imgSrc'],
    data() {
        return {
            isLeft: this.$props.pictureSide === 'left' ? 'fade-left' : 'fade-right'
        }
    },
    methods: {
        ChangePage() {
            this.$router.push({ name: this.$props.buttonPageLink});
        },
    },
}
</script>

<style scoped>

.feature-section-container {
    display: flex;
    margin: 200px auto 0px;
    width: 80%;
}

.image-section {
    flex: 2;
    position: relative;
    width: 400px;
    height: 400px;
}

.image-section img {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    margin: auto;
}

.image-section .image {
    max-height: 450px;
}

.info-section {
    flex: 3;
}

.info-section h2 {
    font-size: 4rem;
    margin-bottom: 1em;
}

.info-section h4 {
    margin-bottom: 1em;
    font-size: 1.8rem;
    width: 70%;
}

.info-section-right {
    margin-left: 100px;
    text-align: right;
    direction: rtl;
}

.info-section-left {
    margin-right: 100px;
}

.info-section-button {
    width: 30%;
    min-width: 200px;
    font-size: 1.3rem;
    font-style: bold;
    font-weight: 800;
}
@media (max-width: 1000px){

.feature-section-container {
    margin: 4em auto 4em;
    flex-wrap: wrap;
}

.image-section img {
    max-height: 300px;
    max-width: 250px;
    display: block;
    margin: auto;
}

.info-section-right, .info-section-left {
    text-align: center;
    margin: 1em 0px 1em;
    flex:2;
}

.info-section-right {
    margin-left: 50px;
}

.info-section-left {
    margin-right: 50px;
}

.info-section > h4 {
    margin-bottom: 1em;
    width: 100%;
    font-size: 1.25rem;
}

.info-section > h2 {
    margin-bottom: 0.5em;
    font-size: 3rem;
}

.info-section-button {
    width: 70%;
    font-size: 1rem;
    border-radius: 0.5em;
    margin-bottom: 1em;
}
.image-section {
    width: auto;
    height: auto;
}
}
@media (max-width: 650px){

.feature-section-container {
    flex-direction: column;
}

.image-section {
    order: 2;
    position: static;
}

.image-section img {
    position: static;
}

.info-section-right, .info-section-left {
    text-align: center;
    margin: 1em 0px 1em;
}

}
</style>