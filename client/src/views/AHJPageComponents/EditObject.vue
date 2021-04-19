<template>
    <div ref="eobj" id="edit-object">
        <h3>{{this.data.DateRequested}}</h3>
        <h3>Changed "{{this.data.OldValue == null || this.data.OldValue == "" ? "None" : this.data.OldValue}}" to "{{this.data.NewValue}}"</h3>
        <h3>Comments: "{{this.data.Comments == "" || this.data.Comments == null ? "No Comments" : this.data.Comments}}"</h3>
        <h3>{{this.data.ChangedBy ? this.data.ChangedBy.Username : "Anonymous"}}</h3>
        <div>
            <i style="margin-right:10px" v-if="$parent.isManaged && this.data.ReviewStatus==='P'" v-on:click="$emit('official',{Type:'Accept',eID: data.EditID});data.ReviewStatus='A';changeStatus();" class="fa fa-check"></i>
            <i v-if="$parent.isManaged && this.data.ReviewStatus==='P'" v-on:click="$emit('official', {Type:'Reject',eID: data.EditID});data.ReviewStatus='R';changeStatus()" class="fa fa-thumbs-down"></i>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        data: {
            type: Object
        }
    },
    mounted: function(){
        this.changeStatus();
    },
    methods: {
        changeStatus(){
                if(this.data.ReviewStatus === 'A'){
                    this.$refs.eobj.style.backgroundColor = "green";
                }
                if(this.data.ReviewStatus === 'R'){
                    this.$refs.eobj.style.backgroundColor = "red";
                }
        },
    }
}
</script>

<style scoped>
#edit-object{
    display: flex;
    justify-content: space-between;
    align-content: center;
    align-items: center;
    padding: 10px;
    background-clip: content-box;
    background-color: white;
}
h1,h2,h3{
    font-family: "Roboto Condensed";
    color: #4b4e52;
    width: 20%;
}
h3{
    font-size: 15px;
    margin: 0px;
}
#content-body{
    display: flex;
    flex-direction: column;
}
</style>