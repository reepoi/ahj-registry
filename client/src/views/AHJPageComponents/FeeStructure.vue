<template>
    <div ref="fs" class="feestr">
        <div class="header">
            <h2 v-if="!isEditing"> {{ (this.data.FeeStructureName === null || this.data.FeeStructureName.Value === "") ? "Unspecified" : this.data.FeeStructureName.Value}}</h2>
            <h3 v-else class="head"><input v-if="isEditing" type="text" v-model="Edits.FeeStructureName" /></h3>
            <div style="display:flex">
            <div style="width: 50px;margin-right:10px;" v-if="eID >= 0">
                <i style="margin-right:10px;margin-top:10px;" v-if="$parent.isManaged && this.editstatus==='P'" v-on:click="$emit('official',{Type:'Accept',eID: eID});editstatus = 'A';changeStatus();" class="fa fa-check"></i>
                <i style="margin-right:5px;" v-if="$parent.isManaged && this.editstatus==='P'" v-on:click="$emit('official',{Type:'Reject',eID: eID});editstatus='R';changeStatus();" class="fa fa-times"></i>
            </div>
            <i ref='chev' style="height:100%;margin-right: 10px;margin-top:10px;" class="fa fa-chevron-down" v-on:click="showInfo()"></i>
            <div style="float: right;" v-if="isEditing">
                <i v-if="!isDeleted" ref='del' style="margin-right: 10px;margin-top:10px;" v-on:click="isDeleted = true" class="fa fa-minus"></i>
                <i v-else v-on:click="isDeleted=false" style="margin-right: 10px;margin-top:10px;" class="fas fa-exclamation-triangle"></i>
            </div>
            </div>
        </div>
        <div style="width:100%;" ref="hidden" class="hide">
            <div style="width:100%;" class="body">
            <h3> ID: {{ (this.data.FeeStructureID === null || this.data.FeeStructureID.Value === "") && !this.isEditing ? "Unspecified" : this.isEditing ? "" : this.data.FeeStructureID.Value}} <input v-if="isEditing" type="text" v-model="Edits.FeeStructureID" /></h3>
            <h3> Fee Structure Type: {{ (this.data.FeeStructureType === null || this.data.FeeStructureType.Value === "") && !this.isEditing ? "Unspecified" : this.isEditing ? "" : this.data.FeeStructureType.Value}} <b-form-select size="sm" style="width:200px;" v-if="isEditing" v-model="Edits.FeeStructureType" :options="consts.CHOICE_FIELDS.FeeStructure.FeeStructureType"/> </h3>
            <h3> Description: {{ (this.data.Description=== null || this.data.Description.Value === "") && !this.isEditing ? "Unspecified" : this.isEditing ? "" : this.data.Description.Value}} <input v-if="isEditing" type="text" v-model="Edits.Description" /> </h3>
            </div>
        </div>
    </div>
</template>

<script>
import constants from '../../constants.js';

export default {
    props: {
        data: {
            type: Object
        },
        editing: {
            type: Boolean
        },
        eID: {
            type: Number,
            default: -1
        },
        editStatus: {
            type: String,
            default: 'A'
        }
    },
    created: function(){
        this.clearEdits();
        this.ID = this.data.FeeStructurePK.Value;
    },
    mounted: function(){
        this.changeStatus();
    },
    data(){
        return {
            Edits: {
                FeeStructureName: "",
                FeeStructureType: "",
                Description: "",
                FeeStructureID: "",
            },
            isEditing: this.editing,
            Type: "FeeStructure",
            consts: constants,
            isDeleted: false,
            ID: -1,
            editstatus: this.editStatus
        }
    },
    watch: {
        '$parent.isEditing': function() {
            this.isEditing = this.$parent.isEditing;
        }
    },
    methods:{
        getEditObjects(){
            return [];
        },
        clearEdits(){
            let k = Object.keys(this.Edits);
            for(let i = 0; i < k.length; i++){
                this.Edits[k[i]] = this.data[k[i]].Value;
            }
            this.isDeleted = false;
        },
        changeStatus(){
            if(this.eID >= 0){
                if(this.editStatus === 'A'){
                    this.$refs.fs.style.backgroundColor = "green";
                }
                if(this.editStatus === 'R'){
                    this.$refs.fs.style.backgroundColor = "red";
                }
            
            }
        },
        showInfo(){
            this.$refs.hidden.classList.toggle('show');
            this.$refs.hidden.classList.toggle('hide');
            this.$refs.chev.classList.toggle('fa-chevron-down');
            this.$refs.chev.classList.toggle('fa-chevron-up');
        },
    }
}
</script>

<style scoped>
.feestr{
    display: flex;
    align-items: center;
    flex-direction: column;
    background-color: white;
}
h3, a{
  font-size: 15px;
  margin: 0px;
}
.header{
    width: 100%;
    border-bottom: 1px solid black;
    text-align: center;
    height: 40px;
    display: flex;
    justify-content: space-between;
}
h2{
    margin: 0;
    width: calc(100% - 200px);
    margin-left: 100px;
    float: left;
}
.head{
    margin: 0;
    width: calc(100% - 200px);
    margin-left: 100px;
    float: left;
}
.hide{
    display: none;
}
.show{
    display: flex;
}
.body{
    display: flex;
    align-items: center;
    flex-direction: column;
    border-bottom: 1px solid black;
}
</style>