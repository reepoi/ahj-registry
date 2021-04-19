<template>
    <div>
        <!-- <p>Commented on AHJ {{ActivityData.AHJPK.Value}}</p> -->
        <p>
            <span class="row-element">Commented on an AHJ, saying:</span>  
        </p>
        <p> {{ActivityData.CommentText.Value}}</p>
    </div>
</template>
<script>
export default {
    props: ['ActivityData'],
}
</script>

<style scoped>

</style>