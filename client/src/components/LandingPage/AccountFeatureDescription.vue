<template>
    <div class="account-feature-container">
        <h2>{{headerText}}</h2>
        <h4>{{paragraphText}}</h4>
        <img :src="require('@/assets/' + imgSrc + '')">
    </div>
</template>

<script>
export default {
    props: ['headerText', 'paragraphText', 'imgSrc']
}
</script>

<style scoped>
.account-feature-container {
    display: flex;
    flex-direction: column;
    max-width: 400px;
    margin: auto 10px;
    text-align: center;
}

.account-feature-container > h2 {
    margin-bottom: 40px;
    font-size: 2.5rem;
}
.account-feature-container > h4 {
    width: 80%;
    margin: auto;
}

.account-feature-container > img{
    max-width: 150px;
    max-height: 150px;
    margin: 50px auto 50px;
}
@media (max-width: 1000px){

.account-feature-container > h4 {
    width: 100%;
    margin: auto;
}
.account-feature-container {
    display: flex;
    flex:1;
    flex-direction: column;
    margin: auto 20px;
    text-align: center;
}
.account-feature-container > img{
    max-width: 100px;
    margin: 50px auto 50px;
}
}

@media (max-width: 1000px){
.account-feature-container > h2 {
    margin-bottom: 20px;
}

.account-feature-container > img {
    margin-top: 20px;
    margin-bottom: 60px;
}

}
</style>