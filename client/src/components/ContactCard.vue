<template>
    <div ref="cc" id="contactCard">
        <div id="header">
            <h2 v-if="!isEditing" style="margin-left: 5px;">{{this.data.FirstName.Value + " " + this.data.LastName.Value}}</h2>
            <div v-else style="display:flex;width:100%;flex-wrap:wrap;">
                <input style="flex-basis:33%;" type="text" v-model="Edits.FirstName">
                <input style="flex-basis:33%;" type="text" v-model="Edits.MiddleName">
                <input style="flex-basis:33%;" type="text" v-model="Edits.LastName">
            </div>
            <div style="display:flex;">
                            <div v-if="eID >= 0">
            <i style="margin-right:10px" v-if="$parent.isManaged && editstatus==='P'" v-on:click="$emit('official',{Type:'Accept',eID: eID});editstatus = 'A';changeStatus();" class="fa fa-check"></i>
            <i style="margin-right:10px" v-if="$parent.isManaged && editstatus==='P'" v-on:click="$emit('official',{Type:'Reject',eID: eID});editstatus='R';changeStatus()" class="fa fa-thumbs-down"></i>
            </div>
            <div style="display:flex;" v-if="isEditing">
                <i ref='chev' style="height:100%;margin-right: 10px;" class="fa fa-chevron-down" v-on:click="showInfo('c-info')"></i>
                <i v-if="!isDeleted" ref='del' style="height:100%;margin-right: 10px;" v-on:click="isDeleted = true" class="fa fa-minus"></i>
                <i v-else v-on:click="isDeleted=false" style="height:100%;margin-right: 10px;" class="fas fa-exclamation-triangle"></i>
            </div>
            <div v-else>
                <i ref='chev' style="height:100%;margin-right: 10px;" class="fa fa-chevron-down" v-on:click="showInfo('c-info')"></i>
            </div>
            </div>
        </div>
        <div ref="c_info" class="hide">
            <div class='title-div'>
                <h3 style="margin:0px;" v-if="!isEditing"> {{this.data.Title === null ? "No Title" : this.data.Title.Value}} </h3>
                <input v-else type="text" v-model="Edits.Title"/>
            </div>
            <div class='info-div'>
                <div class='phone-info'>
                    <h3> Home Phone: {{(this.data.HomePhone === null || this.data.HomePhone.Value === "") && !this.isEditing ? "Unspecified" : this.isEditing ? "" : this.data.HomePhone.Value}}<input v-if="isEditing" v-model="Edits.HomePhone"/>  </h3>
                    <h3> Mobile Phone: {{(this.data.MobilePhone === null || this.data.MobilePhone.Value === "") && !this.isEditing ? "Unspecified" : this.isEditing ? "" : this.data.MobilePhone.Value}}<input v-if="isEditing" v-model="Edits.MobilePhone"/> </h3>
                    <h3> Work Phone: {{(this.data.WorkPhone === null || this.data.WorkPhone.Value === "") && !this.isEditing ? "Unspecified" : this.isEditing ? "" : this.data.WorkPhone.Value}}<input v-if="isEditing" v-model="Edits.WorkPhone"/></h3>
                    <h3> URL: {{(this.data.URL === null || this.data.URL.Value === "") && !this.isEditing ? "Unspecified" : this.isEditing ? "" : this.data.URL.Value}}<input v-if="isEditing" v-model="Edits.URL"/></h3>
                    <h3> Email: {{(this.data.Email === null || this.data.Email.Value === "") && !this.isEditing ? "Unspecified" : this.isEditing ? "" : this.data.Email.Value}}<input v-if="isEditing" v-model="Edits.Email"/> </h3>
                    <h3> Preferred Contact Method: {{(this.data.PreferredContactMethod === null || this.data.PreferredContactMethod.Value === "") && !this.isEditing ? "Unspecified" : this.isEditing ? "" : this.data.PreferredContactMethod.Value}}<input v-if="isEditing" v-model="Edits.PreferredContactMethod"/> </h3>
                </div>
                <div id="addr" class='addr-info'>
                    <h3 class="desc" v-if="this.AddressString !== ''">{{this.AddressString}}</h3>
                    <h3 class="desc" v-else>No Address Provided</h3>
                </div>
                <div class="desc">
                    <h3>{{(this.data.Description === null || this.data.Description.Value === "") && !this.isEditing ? "Unspecified" : this.isEditing ? "" : this.data.Description.Value}}<input v-if="isEditing" v-model="Edits.Description"/></h3>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

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
        },
    },
    data() {
        return {
            isEditing: this.editing,
            AddressString: "",
            CityCountyState: "",
            isDeleted: false,
            Type: "Contact",
            editable: true,
            ID: -1,
            Edits: {
                Title: this.data.Title ? this.data.Title.Value : "",
                HomePhone: this.data.HomePhone ? this.data.HomePhone.Value : "",
                MobilePhone: "",
                WorkPhone: "",
                URL: "",
                Email: "",
                PreferredContactMethod: "",
                Description: "",
                FirstName: "",
                MiddleName: "",
                LastName: ""
            },
            editstatus: this.editStatus
        }
    },
    created: function(){
        // let k = Object.keys(this.data);
        // for(let i = 0; i < k.length; i++){
        //     if(k[i] === "Address"){
        //         continue;
        //     }
        //     if(this.data[k[i]] === null){
        //         if(k[i] === 'MiddleName'){
        //             continue;
        //         }
        //         this.data[k[i]] = { Value: ""};
        //         continue;
        //     }
        // }
    },
    mounted: function() {
        this.$nextTick(()=>{
        if(this.data.Address){
            this.formatAddress(this.data.Address);
        }
        // this.ID = this.data.ContactID.Value;
        this.clearEdits();
        });
        this.changeStatus();
        this.ID = this.data.ContactID.Value;
    },
    methods:{
        showInfo(){
            this.$refs.c_info.classList.toggle('show');
            this.$refs.c_info.classList.toggle('hide');
            this.$refs.chev.classList.toggle('fa-chevron-down');
            this.$refs.chev.classList.toggle('fa-chevron-up');
        },
        changeStatus(){
            if(this.eID >= 0){
                if(this.editstatus === 'A'){
                    this.$refs.cc.style.backgroundColor = "green";
                }
                if(this.editstatus === 'R'){
                    this.$refs.cc.style.backgroundColor = "red";
                }
            
            }
        },
        formatAddress(Address){
                if(Address.AddrLine1 !== null){
                    this.AddressString += Address.AddrLine1.Value;
                }
                if(Address.AddrLine2 !== null){
                    if(this.AddressString !== ""){
                        this.AddressString += ', ';
                    }
                    this.AddressString += Address.AddrLine2.Value;
                }
                if(Address.AddrLine3 !== null){
                    if(this.AddressString !== ""){
                        this.AddressString += ', '
                    }
                    this.AddressString += Address.AddrLine3.Value;
                }
                this.CityCountyState = "";
            if(this.AddressString !== ""){
                this.CityCountyState += ', ';
            }
            if(Address.City.Value !== null){
                this.CityCountyState += Address.City.Value;
            }
            if(Address.County !== null){
                if(Address.City.Value !== ""){
                    this.CityCountyState += ", "
                }
                this.CityCountyState += Address.County.Value;
            }
            if(Address.StateProvince !== null){
                if(Address.County.Value !== ""){
                    this.CityCountyState += ", "
                }
                this.CityCountyState += Address.StateProvince.Value;
            }
            if(Address.Country !== null){
                if(Address.StateProvince.Value !== ""){
                    this.CityCountyState += ", "
                }
                this.CityCountyState += Address.Country.Value;
            }
            if(Address.ZipPostalCode !== null){
                if(Address.Country.Value !== ""){
                    this.CityCountyState += ", "
                }
                this.CityCountyState += Address.ZipPostalCode.Value;
            }
            this.AddressString = this.AddressString + this.CityCountyState;
        },
        clearEdits(){
            let keys = Object.keys(this.Edits);
            for(let i = 0; i < keys.length; i++){
                this.Edits[keys[i]] = this.data[keys[i]].Value;
            }
            this.isDeleted = false;
        },
        getEditObjects(){
            return [];
        }
    },
    watch: {
        '$parent.isEditing': function() {
            this.isEditing = this.$parent.isEditing;
        }
    }
}
</script>

<style scoped>
h1,h2,h3{
    font-family: "Roboto Condensed";
    color: #4b4e52;
}
h3{
    font-size: 10px;
    margin: 0px;
}
.info-header{
    font-size: 10px;
    margin: 0px;
}
#contactCard{
    position: relative;
    width: 100%;
    margin: 0;
    display: flex;
    flex-direction: column;
    border-bottom: 1px solid black;
    background-color: white;
}
#header{
    display: flex;
    align-items: center;
    justify-content: space-between;
}
#c-info{
    position: relative;
    width: 100%;
    border-top: 1px solid black;
    background-color: white;
}
.show{
    display: table;
}
.hide{
    display: none;
}
.title-div{
    position: relative;
    border-bottom: 1px solid gray;
    border-top: 1px solid black;
}
.phone-info{
    position: relative;
    width: 100%;
    display: flex;
    justify-content: center;
    flex-direction: column;
    align-items: center;
}
.addr-info{
    position: relative;
    width: 100%;
}
.info-div{
    position: relative;
    width: 100%;
    overflow: auto;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
}
.no-data{
    padding-top: 11%;
}
.desc{
    text-align: center;
    width: 100%;
    border-top: 1px solid gray;
}
.bb{
    border-bottom: 1px solid black;
}
</style>