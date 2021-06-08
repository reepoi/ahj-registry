<template>
  <div class="setting-page-container">
    <div class="settings-module">
      <div class="settings-sidebar">
        <!-- Sidebar for all settings buttons that the user can use to navigate between settings modules. -->
          <b-button-group id="settings-button-group">
            <b-button class="settings-button selected-button" id="edit-profile-button" variant="outline-secondary" @click="ChangeSelectedComponent('EditProfile')"> Edit Profile </b-button>
            <b-button class="settings-button" id="change-password-button" variant="outline-secondary" @click="ChangeSelectedComponent('ChangePassword')"> Change Password </b-button>
            <b-button class="settings-button" id="account-privileges-button" variant="outline-secondary" @click="ChangeSelectedComponent('AccountPrivileges')"> Account Privileges </b-button>
            <b-button class="settings-button" id="api-button" variant="outline-secondary" @click="ChangeSelectedComponent('API')"> API </b-button>
          </b-button-group>
      </div>
      <!-- active setting component -->
      <div class="settings-selected-component">
        <div class="component-form">
          <edit-profile v-if="this.selectedComponent==='EditProfile'"></edit-profile>
          <change-password v-if="this.selectedComponent==='ChangePassword'"></change-password>
          <account-privileges v-if="this.selectedComponent==='AccountPrivileges'"></account-privileges>
          <api v-if="this.selectedComponent==='API'"></api>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EditProfile from "../../components/UserAccounts/UserSettings/EditProfile.vue"
import ChangePassword from "../../components/UserAccounts/UserSettings/ChangePassword.vue"
import AccountPrivileges from "../../components/UserAccounts/UserSettings/AccountPrivileges.vue"
import API from "../../components/UserAccounts/UserSettings/API.vue"
export default {
  data() {
    return {
      profileInfo: {},
      selectedComponent: 'EditProfile'
    }
  },
  components: {
    "edit-profile": EditProfile,
    "change-password": ChangePassword,
    "account-privileges": AccountPrivileges,
    "api": API
  },
  methods: {
      // Changes the selected component variable (which changes the active settings module) and updates which button has the 'selected' css styling
      ChangeSelectedComponent(selectedComponent) {
        if (selectedComponent === this.selectedComponent)
            return;

        this.selectedComponent = selectedComponent;

        let currSelectedButton = document.getElementsByClassName("selected-button")[0];
        currSelectedButton.classList.remove('selected-button');
        switch(selectedComponent){
          case 'ChangePassword':
            currSelectedButton = document.getElementById('change-password-button');
            break;
          case 'AccountPrivileges':
            currSelectedButton = document.getElementById('account-privileges-button');
            break;
          case 'API':
            currSelectedButton = document.getElementById('api-button');
            break;
          case 'EditProfile':
          default:
            currSelectedButton = document.getElementById('edit-profile-button');
        }
        currSelectedButton.classList.add('selected-button');
      }
  },
};
</script>

<style scoped>
.setting-page-container {
  background-color: #f2f5f7;
}

.settings-module {
  width: 70%;
  min-height: 30em;
  margin: 3.2em auto;
  background-color: white;
  display: grid;
  grid-template-columns: auto;
  grid-template-rows: auto auto;
  border: 1px solid #D3D3D3;
}

.settings-sidebar {
  grid-column: 1 / 2;
  border-bottom: 1px solid #D3D3D3;
}

#settings-button-group {
  width: 100%;
}

.settings-button {
  width: 100%;
  border: none;
  font-size: 1.5rem;
}

.settings-button:hover {
  background-color: lightgray !important;
  color: #71757d !important;
}

.selected-button {
  border-top: thick solid gray;
  background-color: #ECECEC !important;
  font-weight: 800;
}

.settings-selected-component {
  grid-column: 2 / 3;
  min-height: 500px;
}

.component-form {
  width: 80%;
  margin: 3.2em auto;
}

.settings-sidebar {
  grid-row: 1 / 2;
  grid-column: 1;
}

.settings-selected-component {
  grid-row: 2 / 3;
  grid-column: 1;
  width: 80%;
  margin: auto;
}

@media (max-width: 1000px){
  .settings-module {
    width: 90%;
  }
}
@media (max-width: 650px){
  .settings-button {
      font-size: 1.2rem;
  }
  .component-form {
    width: 100%;
  }
}

</style>
