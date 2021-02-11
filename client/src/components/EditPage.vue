<template>
  <b-container>
    <b-row>
      <b-col>
        <b-button v-if="editPageViewOnly" size="sm" variant="danger" @click="tryEnterEditPageEditMode">Edit this AHJ</b-button>
      </b-col>
    </b-row>
    <b-row v-if="recordLoading">
      <div class="text-center text-primary my-2">
        <b-spinner class="align-middle"></b-spinner>
        <strong>&nbsp; Loading...</strong>
      </div>
    </b-row>
    <b-row v-else>
      <b-col>
        <b-form @submit.prevent="onSubmit" @reset.prevent="onReset">
            <b-tabs card>
              <b-tab title="AHJ" active>
                  <b-form-group id="input-group-1" label-for="input-1">
                    <b-tabs card>
                      <b-card-header header-tag="header" class="p-0" role="tab">
                        <b-button block v-b-toggle.accordion-1 variant="info">AHJ Information</b-button>
                      </b-card-header>
                      <b-collapse id="accordion-1" visible accordion="my-accordion" role="tabpanel">
                        <b-card-body>
                        <div v-for="(valueAHJ, nameAHJ) in constants.AHJ_FIELDS" :key=nameAHJ>
                          <b-row v-if="!isObject(AHJ[nameAHJ]) && (mode === 'create' ? nameAHJ !== 'RecordID' : true)">
                            <b-col cols="4">
                              <label>{{ nameAHJ === "RecordID" ? "AHJ ID" : formatFieldNames(nameAHJ) }}:</label>
                            </b-col>
                            <b-col v-if="editPageViewOnly">
                              <label>{{ AHJ[nameAHJ] }}</label>
                            </b-col>
                            <b-col cols="8" v-else>
                              <label v-if="nameAHJ === 'RecordID' || nameAHJ === 'AHJCode'">{{ AHJ[nameAHJ] }}</label>
                              <b-form-select v-else-if="choiceFields.AHJ[nameAHJ]" v-model="AHJ[nameAHJ]" :options="choiceFields.AHJ[nameAHJ]" />
                              <b-form-input v-else v-model="AHJ[nameAHJ]" type="text" :placeholder="getBFormInputPlaceholder(nameAHJ)" />
                            </b-col>
                          </b-row>
                        </div>
                        <b-row>
                          <b-col>
                            <b-button v-if="!editPageViewOnly && AHJ.Address === null" @click="addAddress(AHJ)">Add Address</b-button>
                          </b-col>
                        </b-row>
                        </b-card-body>
                      </b-collapse>
                      <div v-if="AHJ.Address">
                        <b-card-header header-tag="header" class="p-0" role="tab">
                          <b-button block v-b-toggle.accordion-2 variant="info">Address</b-button>
                        </b-card-header>
                        <b-collapse id="accordion-2" accordion="my-accordion" role="tabpanel">
                          <b-card-body>
                              <div v-for="(valueAHJAddress, nameAHJAddress) in constants.ADDRESS_FIELDS" :key=nameAHJAddress>
                                <b-row v-if="!isObject(AHJ.Address[nameAHJAddress]) && (mode === 'create' ? nameAHJAddress !== 'RecordID' : true)">
                                  <b-col cols="4">
                                    <label>{{ nameAHJAddress === "RecordID" ? "Address ID" : formatFieldNames(nameAHJAddress) }}:</label>
                                  </b-col>
                                  <b-col v-if="editPageViewOnly">
                                    <label>{{ AHJ.Address[nameAHJAddress] }}</label>
                                  </b-col>
                                  <b-col cols="8" v-else>
                                    <label v-if="nameAHJAddress === 'RecordID'">{{ AHJ.Address[nameAHJAddress] }}</label>
                                    <b-form-select v-else-if="choiceFields.Address[nameAHJAddress]" v-model="AHJ.Address[nameAHJAddress]" :options="choiceFields.Address[nameAHJAddress]" />
                                    <b-form-input v-else v-model="AHJ.Address[nameAHJAddress]" type="text" :placeholder="getBFormInputPlaceholder(nameAHJAddress)" />
                                  </b-col>
                                </b-row>
                              </div>
                              <b-row>
                                <b-col>
                                  <b-button v-if="!editPageViewOnly && AHJ.Address.Location === null" @click="addLocation(AHJ.Address)">Add Location</b-button>
                                </b-col>
                              </b-row>
                          </b-card-body>
                        </b-collapse>
                      </div>
                      <div v-if="AHJ.Address && AHJ.Address.Location">
                        <b-card-header header-tag="header" class="p-0" role="tab">
                          <b-button block v-b-toggle.accordion-3 variant="info">Location</b-button>
                        </b-card-header>
                        <b-collapse id="accordion-3" accordion="my-accordion" role="tabpanel">
                          <b-card-body>
                            <div v-for="(valueAHJAddressLocation, nameAHJAddressLocation) in constants.LOCATION_FIELDS" :key=nameAHJAddressLocation>
                              <b-row v-if="mode === 'create' ? nameAHJAddressLocation !== 'RecordID' : true">
                                <b-col cols="4">
                                  <label>{{ nameAHJAddressLocation === "RecordID" ? "Location ID" : formatFieldNames(nameAHJAddressLocation)  }}:</label>
                                </b-col>
                                <b-col v-if="editPageViewOnly">
                                  <label>{{ AHJ.Address.Location[nameAHJAddressLocation] }}</label>
                                </b-col>
                                <b-col cols="8" v-else>
                                  <label v-if="nameAHJAddressLocation === 'RecordID'">{{ AHJ.Address.Location[nameAHJAddressLocation] }}</label>
                                  <b-form-select v-else-if="choiceFields.Location[nameAHJAddressLocation]" v-model="AHJ.Address.Location[nameAHJAddressLocation]" :options="choiceFields.Location[nameAHJAddressLocation]" />
                                  <b-form-input v-else v-model="AHJ.Address.Location[nameAHJAddressLocation]" type="text" :placeholder="getBFormInputPlaceholder(nameAHJAddressLocation)" />
                                </b-col>
                              </b-row>
                            </div>
                          </b-card-body>
                        </b-collapse>
                      </div>
                    </b-tabs>
                  </b-form-group>
              </b-tab>
              <b-tab title="Contacts">
                <b-form-group id="input-group-1" label-for="input-1">
                  <b-tabs card>
                    <b-tab v-for="i in tabsContact" :key="'dyn-tab-' + i" :title="'Contact ' + getTabTitle('Contacts[' + i + ']')">
                      <b-button size="sm" variant="danger" class="float-right" :disabled="editPageViewOnly" @click="closeTabContact(i)">Delete</b-button>
                      <b-card-header header-tag="header" class="p-0" role="tab">
                        <b-button block v-b-toggle.accordion-4 variant="info">Contact Information</b-button>
                      </b-card-header>
                      <b-collapse id="accordion-4" visible accordion="my-accordion-contact" role="tabpanel">
                        <b-card-body>
                          <div v-for="(valueContact, nameContact) in constants.CONTACT_FIELDS" :key=nameContact>
                            <b-row v-if="!isObject(AHJ.Contacts[i][nameContact]) && (mode === 'create' ? nameContact !== 'RecordID' : true)">
                              <b-col cols="4">
                                <label>{{ nameContact === "RecordID" ? "Contact ID" : formatFieldNames(nameContact)  }}:</label>
                              </b-col>
                              <b-col v-if="editPageViewOnly">
                                <label>{{ AHJ.Contacts[i][nameContact] }}</label>
                              </b-col>
                              <b-col cols="8" v-else>
                                <label v-if="nameContact === 'RecordID'">{{ AHJ.Contacts[i][nameContact] }}</label>
                                <b-form-select v-else-if="choiceFields.Contact[nameContact]" v-model="AHJ.Contacts[i][nameContact]" :options="choiceFields.Contact[nameContact]" />
                                <b-form-input v-else v-model="AHJ.Contacts[i][nameContact]" type="text" :placeholder="getBFormInputPlaceholder(nameContact)" />
                              </b-col>
                            </b-row>
                          </div>
                          <b-row>
                            <b-col>
                              <b-button v-if="!editPageViewOnly && AHJ.Contacts[i].Address === null" @click="addAddress(AHJ.Contacts[i])">Add Address</b-button>
                            </b-col>
                          </b-row>
                        </b-card-body>
                      </b-collapse>
                      <div v-if="AHJ.Contacts[i].Address">
                        <b-card-header header-tag="header" class="p-0" role="tab">
                          <b-button block v-b-toggle.accordion-5 variant="info">Address</b-button>
                        </b-card-header>
                        <b-collapse id="accordion-5" accordion="my-accordion-contact" role="tabpanel">
                          <b-card-body>
                          <div v-for="(valueContactAddress, nameContactAddress) in constants.ADDRESS_FIELDS" :key=nameContactAddress>
                            <b-row v-if="!isObject(AHJ.Contacts[i].Address[nameContactAddress]) && (mode === 'create' ? nameContactAddress !== 'RecordID' : true)">
                              <b-col cols="4">
                                <label>{{ nameContactAddress === "RecordID" ? "Address ID" : formatFieldNames(nameContactAddress) }}:</label>
                              </b-col>
                              <b-col v-if="editPageViewOnly">
                                <label>{{ AHJ.Contacts[i].Address[nameContactAddress] }}</label>
                              </b-col>
                              <b-col cols="8" v-else>
                                <label v-if="nameContactAddress === 'RecordID'">{{ AHJ.Contacts[i].Address[nameContactAddress] }}</label>
                                <b-form-select v-else-if="choiceFields.Address[nameContactAddress]" v-model="AHJ.Contacts[i].Address[nameContactAddress]" :options="choiceFields.Address[nameContactAddress]" />
                                <b-form-input v-else v-model="AHJ.Contacts[i].Address[nameContactAddress]" type="text" :placeholder="getBFormInputPlaceholder(nameContactAddress)" />
                                  </b-col>
                                </b-row>
                              </div>
                              <b-row>
                                <b-col>
                                  <b-button v-if="!editPageViewOnly && AHJ.Contacts[i].Address.Location === null" @click="addLocation(AHJ.Contacts[i].Address)">Add Location</b-button>
                                </b-col>
                              </b-row>
                          </b-card-body>
                        </b-collapse>
                      </div>
                      <div v-if="AHJ.Contacts[i].Address && AHJ.Contacts[i].Address.Location">
                        <b-card-header header-tag="header" class="p-0" role="tab">
                          <b-button block v-b-toggle.accordion-6 variant="info">Location</b-button>
                        </b-card-header>
                        <b-collapse id="accordion-6" accordion="my-accordion-contact" role="tabpanel">
                          <b-card-body>
                            <div v-for="(valueContactAddressLocation, nameContactAddressLocation) in constants.LOCATION_FIELDS" :key=nameContactAddressLocation>
                              <b-row v-if="mode === 'create' ? nameContactAddressLocation !== 'RecordID' : true">
                                <b-col cols="4">
                                  <label>{{ nameContactAddressLocation === "RecordID" ? "Location ID" : formatFieldNames(nameContactAddressLocation)  }}:</label>
                                </b-col>
                                <b-col v-if="editPageViewOnly">
                                  <label>{{ AHJ.Contacts[i].Address.Location[nameContactAddressLocation] }}</label>
                                </b-col>
                                <b-col cols="8" v-else>
                                  <label v-if="nameContactAddressLocation === 'RecordID'">{{ AHJ.Contacts[i].Address.Location[nameContactAddressLocation] }}</label>
                                  <b-form-select v-else-if="choiceFields.Location[nameContactAddressLocation]" v-model="AHJ.Contacts[i].Address.Location[nameContactAddressLocation]" :options="choiceFields.Location[nameContactAddressLocation]" />
                                  <b-form-input v-else v-model="AHJ.Contacts[i].Address.Location[nameContactAddressLocation]" type="text" :placeholder="getBFormInputPlaceholder(nameContactAddressLocation)" />
                                </b-col>
                              </b-row>
                            </div>
                          </b-card-body>
                        </b-collapse>
                      </div>
                    </b-tab>
                    <template v-slot:tabs-end>
                      <b-nav-item role="presentation" :disabled="editPageViewOnly" @click.prevent="newTabContact" href="#"><b>+</b></b-nav-item>
                    </template>
                  </b-tabs>
                </b-form-group>
              </b-tab>
              <b-tab title="Engineering Review Requirements">
                <b-form-group
                      id="input-group-1"
                      label-for="input-1"
                    >
                  <b-tabs card>
                    <b-tab v-for="i in tabsEngReqRev" :key="'dyn-tab-' + i" :title="'Engineering Review Requirement ' + getTabTitle('EngineeringReviewRequirements[' + i + ']')">
                      <b-row>
                        <b-col>
                          <b-button size="sm" variant="danger" class="float-right" :disabled="editPageViewOnly" @click="closeTabEngReqReq(i)">Delete</b-button>
                        </b-col>
                      </b-row>
                      <div v-for="(valueEngRevReq, nameEngRevReq) in constants.ENGINEERINGREVIEWREQUIREMENTS_FIELDS" :key=nameEngRevReq>
                        <b-row v-if="mode === 'create' ? nameEngRevReq !== 'RecordID' : true">
                          <b-col cols="4">
                            <label>{{ nameEngRevReq === "RecordID" ? "Engineering Review Requirement ID" : formatFieldNames(nameEngRevReq) }}:</label>
                          </b-col>
                          <b-col v-if="editPageViewOnly">
                            <label>{{ AHJ.EngineeringReviewRequirements[i][nameEngRevReq] }}</label>
                          </b-col>
                          <b-col cols="8" v-else>
                            <label v-if="nameEngRevReq === 'RecordID'">{{ AHJ.EngineeringReviewRequirements[i][nameEngRevReq] }}</label>
                            <b-form-select v-else-if="choiceFields.EngineeringReviewRequirement[nameEngRevReq]" v-model="AHJ.EngineeringReviewRequirements[i][nameEngRevReq]" :options="choiceFields.EngineeringReviewRequirement[nameEngRevReq]" />
                            <b-form-input v-else v-model="AHJ.EngineeringReviewRequirements[i][nameEngRevReq]" type="text" :placeholder="getBFormInputPlaceholder(nameEngRevReq)" />
                          </b-col>
                        </b-row>
                      </div>
                    </b-tab>
                    <template v-slot:tabs-end>
                      <b-nav-item role="presentation" :disabled="editPageViewOnly" @click.prevent="newTabEngRevReq" href="#"><b>+</b></b-nav-item>
                    </template>
                  </b-tabs>
                </b-form-group>
              </b-tab>
              <b-tab title="AHJ Inspections">
                <b-form-group
                      id="input-group-1"
                      label-for="input-1"
                    >
                  <b-tabs card>
                    <b-tab v-for="i in tabsAHJInspection" :key="'dyn-tab-' + i" :title="'AHJ Inspection ' + getTabTitle('AHJInspections[' + i + ']')">
                      <b-row>
                        <b-col>
                          <b-button size="sm" variant="danger" class="float-right" :disabled="editPageViewOnly" @click="closeTabAHJInspection(i)">Delete</b-button>
                        </b-col>
                      </b-row>
                      <b-card-header header-tag="header" class="p-0" role="tab">
                        <b-button block v-b-toggle.accordion-7 variant="info">AHJ Inspection Information</b-button>
                      </b-card-header>
                      <b-collapse id="accordion-7" visible accordion="my-accordion" role="tabpanel">
                        <b-card-body>
                        <div v-for="(valueAHJInspection, nameAHJInspection) in constants.AHJINSPECTION_FIELDS" :key=nameAHJInspection>
                          <b-row v-if="!isObject(AHJ.AHJInspections[i][nameAHJInspection]) && (mode === 'create' ? nameAHJInspection !== 'RecordID' : true)">
                            <b-col cols="4">
                              <label>{{ nameAHJInspection === "RecordID" ? "AHJ Inspection ID" : formatFieldNames(nameAHJInspection) }}:</label>
                            </b-col>
                            <b-col v-if="editPageViewOnly">
                              <label>{{ AHJ.AHJInspections[i][nameAHJInspection] }}</label>
                            </b-col>
                            <b-col cols="8" v-else>
                              <label v-if="nameAHJInspection === 'RecordID'">{{ AHJ[nameAHJInspection] }}</label>
                              <b-form-select v-else-if="choiceFields.AHJInspection[nameAHJInspection]" v-model="AHJ.AHJInspections[i][nameAHJInspection]" :options="choiceFields.AHJInspection[nameAHJInspection]" />
                              <b-form-input v-else v-model="AHJ.AHJInspections[i][nameAHJInspection]" type="text" :placeholder="getBFormInputPlaceholder(nameAHJInspection)" />
                            </b-col>
                          </b-row>
                        </div>
                        <b-row>
                          <b-col>
                            <b-button v-if="!editPageViewOnly && AHJ.Address === null" @click="addAddress(AHJ)">Add Address</b-button>
                          </b-col>
                        </b-row>
                        </b-card-body>
                      </b-collapse>
                      <b-card-header header-tag="header" class="p-0" role="tab">
                        <b-button block v-b-toggle.accordion-8 variant="info">Contacts</b-button>
                      </b-card-header>
                      <b-collapse id="accordion-8" accordion="my-accordion" role="tabpanel">
                        <b-card-body>
                          <b-form-group id="input-group-1" label-for="input-1">
                            <b-tabs card>
                              <b-tab v-for="j in tabsAHJInspectionsContact[i]" :key="'dyn-tab-' + j" :title="'Contact ' + getTabTitle('AHJInspections[' + i + '].Contacts[' + j + ']')">
                                <b-button size="sm" variant="danger" class="float-right" :disabled="editPageViewOnly" @click="closeTabAHJInspectionContact(i, j)">Delete</b-button>
                                <b-card-header header-tag="header" class="p-0" role="tab">
                                  <b-button block v-b-toggle.accordion-9 variant="info">Contact Information</b-button>
                                </b-card-header>
                                <b-collapse id="accordion-9" visible accordion="my-accordion-contact" role="tabpanel">
                                  <b-card-body>
                                    <div v-for="(valueContact, nameContact) in constants.CONTACT_FIELDS" :key=nameContact>
                                      <b-row v-if="!isObject(AHJ.AHJInspections[i].Contacts[j][nameContact]) && (mode === 'create' ? nameContact !== 'RecordID' : true)">
                                        <b-col cols="4">
                                          <label>{{ nameContact === "RecordID" ? "Contact ID" : formatFieldNames(nameContact)  }}:</label>
                                        </b-col>
                                        <b-col v-if="editPageViewOnly">
                                          <label>{{ AHJ.AHJInspections[i].Contacts[j][nameContact] }}</label>
                                        </b-col>
                                        <b-col cols="8" v-else>
                                          <label v-if="nameContact === 'RecordID'">{{ AHJ.AHJInspections[i].Contacts[j][nameContact] }}</label>
                                          <b-form-select v-else-if="choiceFields.Contact[nameContact]" v-model="AHJ.AHJInspections[i].Contacts[j][nameContact]" :options="choiceFields.Contact[nameContact]" />
                                          <b-form-input v-else v-model="AHJ.AHJInspections[i].Contacts[j][nameContact]" type="text" :placeholder="getBFormInputPlaceholder(nameContact)" />
                                        </b-col>
                                      </b-row>
                                    </div>
                                    <b-row>
                                      <b-col>
                                        <b-button v-if="!editPageViewOnly && AHJ.AHJInspections[i].Contacts[j].Address === null" @click="addAddress(AHJ.AHJInspections[i].Contacts[j])">Add Address</b-button>
                                      </b-col>
                                    </b-row>
                                  </b-card-body>
                                </b-collapse>
                                <div v-if="AHJ.AHJInspections[i].Contacts[j].Address">
                                  <b-card-header header-tag="header" class="p-0" role="tab">
                                    <b-button block v-b-toggle.accordion-10 variant="info">Address</b-button>
                                  </b-card-header>
                                  <b-collapse id="accordion-10" accordion="my-accordion-contact" role="tabpanel">
                                    <b-card-body>
                                    <div v-for="(valueContactAddress, nameContactAddress) in constants.ADDRESS_FIELDS" :key=nameContactAddress>
                                      <b-row v-if="!isObject(AHJ.AHJInspections[i].Contacts[j].Address[nameContactAddress]) && (mode === 'create' ? nameContactAddress !== 'RecordID' : true)">
                                        <b-col cols="4">
                                          <label>{{ nameContactAddress === "RecordID" ? "Address ID" : formatFieldNames(nameContactAddress) }}:</label>
                                        </b-col>
                                        <b-col v-if="editPageViewOnly">
                                          <label>{{ AHJ.AHJInspections[i].Contacts[j].Address[nameContactAddress] }}</label>
                                        </b-col>
                                        <b-col cols="8" v-else>
                                          <label v-if="nameContactAddress === 'RecordID'">{{ AHJ.AHJInspections[i].Contacts[j].Address[nameContactAddress] }}</label>
                                          <b-form-select v-else-if="choiceFields.Address[nameContactAddress]" v-model="AHJ.AHJInspections[i].Contacts[j].Address[nameContactAddress]" :options="choiceFields.Address[nameContactAddress]" />
                                          <b-form-input v-else v-model="AHJ.AHJInspections[i].Contacts[j].Address[nameContactAddress]" type="text" :placeholder="getBFormInputPlaceholder(nameContactAddress)" />
                                            </b-col>
                                          </b-row>
                                        </div>
                                        <b-row>
                                          <b-col>
                                            <b-button v-if="!editPageViewOnly && AHJ.AHJInspections[i].Contacts[j].Address.Location === null" @click="addLocation(AHJ.AHJInspections[i].Contacts[j].Address)">Add Location</b-button>
                                          </b-col>
                                        </b-row>
                                    </b-card-body>
                                  </b-collapse>
                                </div>
                                <div v-if="AHJ.AHJInspections[i].Contacts[j].Address && AHJ.AHJInspections[i].Contacts[j].Address.Location">
                                  <b-card-header header-tag="header" class="p-0" role="tab">
                                    <b-button block v-b-toggle.accordion-11 variant="info">Location</b-button>
                                  </b-card-header>
                                  <b-collapse id="accordion-11" accordion="my-accordion-contact" role="tabpanel">
                                    <b-card-body>
                                      <div v-for="(valueContactAddressLocation, nameContactAddressLocation) in constants.LOCATION_FIELDS" :key=nameContactAddressLocation>
                                        <b-row v-if="mode === 'create' ? nameContactAddressLocation !== 'RecordID' : true">
                                          <b-col cols="4">
                                            <label>{{ nameContactAddressLocation === "RecordID" ? "Location ID" : formatFieldNames(nameContactAddressLocation)  }}:</label>
                                          </b-col>
                                          <b-col v-if="editPageViewOnly">
                                            <label>{{ AHJ.AHJInspections[i].Contacts[j].Address.Location[nameContactAddressLocation] }}</label>
                                          </b-col>
                                          <b-col cols="8" v-else>
                                            <label v-if="nameContactAddressLocation === 'RecordID'">{{ AHJ.AHJInspections[i].Contacts[j].Address.Location[nameContactAddressLocation] }}</label>
                                            <b-form-select v-else-if="choiceFields.Location[nameContactAddressLocation]" v-model="AHJ.AHJInspections[i].Contacts[j].Address.Location[nameContactAddressLocation]" :options="choiceFields.Location[nameContactAddressLocation]" />
                                            <b-form-input v-else v-model="AHJ.AHJInspections[i].Contacts[j].Address.Location[nameContactAddressLocation]" type="text" :placeholder="getBFormInputPlaceholder(nameContactAddressLocation)" />
                                          </b-col>
                                        </b-row>
                                      </div>
                                    </b-card-body>
                                  </b-collapse>
                                </div>
                              </b-tab>
                              <template v-slot:tabs-end>
                                <b-nav-item role="presentation" :disabled="editPageViewOnly" @click.prevent="newTabAHJInspectionContact(i)" href="#"><b>+</b></b-nav-item>
                              </template>
                            </b-tabs>
                          </b-form-group>
                        </b-card-body>
                      </b-collapse>
                    </b-tab>
                    <template v-slot:tabs-end>
                      <b-nav-item role="presentation" :disabled="editPageViewOnly" @click.prevent="newTabAHJInspection" href="#"><b>+</b></b-nav-item>
                    </template>
                  </b-tabs>
                </b-form-group>
              </b-tab>
              <b-tab title="Fee Structures">
                <b-form-group
                      id="input-group-1"
                      label-for="input-1"
                    >
                  <b-tabs card>
                    <b-tab v-for="i in tabsFeeStructure" :key="'dyn-tab-' + i" :title="'Fee Structure ' + getTabTitle('FeeStructures[' + i + ']')">
                      <b-row>
                        <b-col>
                          <b-button size="sm" variant="danger" class="float-right" :disabled="editPageViewOnly" @click="closeTabFeeStructure(i)">Delete</b-button>
                        </b-col>
                      </b-row>
                      <div v-for="(valueFeeStructure, nameFeeStructure) in constants.FEESTRUCTURE_FIELDS" :key=nameFeeStructure>
                        <b-row v-if="mode === 'create' ? nameFeeStructure !== 'RecordID' : true">
                          <b-col cols="4">
                            <label>{{ nameFeeStructure === "RecordID" ? "Fee Structure ID" : formatFieldNames(nameFeeStructure) }}:</label>
                          </b-col>
                          <b-col v-if="editPageViewOnly">
                            <label>{{ AHJ.FeeStructures[i][nameFeeStructure] }}</label>
                          </b-col>
                          <b-col cols="8" v-else>
                            <b-form-input v-if="nameFeeStructure === 'RecordID' && (beforeEditAHJRecord.FeeStructures[i] ? !checkEditMade(beforeEditAHJRecord.FeeStructures[i], AHJ.FeeStructures[i], nameFeeStructure) : true)" v-model="AHJ.FeeStructures[i][nameFeeStructure]" type="text" placeholder="Enter a UUID (leave blank to generate one)..." />
                            <label v-else-if="nameFeeStructure === 'RecordID'">{{ AHJ.FeeStructures[i][nameFeeStructure] }}</label>
                            <b-form-select v-else-if="choiceFields.FeeStructure[nameFeeStructure]" v-model="AHJ.FeeStructures[i][nameFeeStructure]" :options="choiceFields.FeeStructure[nameFeeStructure]" />
                            <b-form-input v-else v-model="AHJ.FeeStructures[i][nameFeeStructure]" type="text" :placeholder="getBFormInputPlaceholder(nameFeeStructure)" />
                          </b-col>
                        </b-row>
                      </div>
                    </b-tab>
                    <template v-slot:tabs-end>
                      <b-nav-item role="presentation" :disabled="editPageViewOnly" @click.prevent="newTabFeeStructure" href="#"><b>+</b></b-nav-item>
                    </template>
                  </b-tabs>
                </b-form-group>
              </b-tab>
              <b-tab title="Document Submission Methods">
                <b-form-group
                      id="input-group-1"
                      label-for="input-1"
                    >
                  <b-tabs card>
                    <b-tab v-for="i in tabsDocSubMethod" :key="'dyn-tab-' + i" :title="'Document Submission Method ' + getTabTitle('DocumentSubmissionMethods[' + i + ']')">
                      <b-row>
                        <b-col>
                          <b-button size="sm" variant="danger" class="float-right" :disabled="editPageViewOnly" @click="closeTabDocSubMethod(i)">Delete</b-button>
                        </b-col>
                      </b-row>
                      <div v-for="(valueDocSubMethod, nameDocSubMethod) in constants.DOCUMENTSUBMISSIONMETHOD_FIELDS" :key=nameDocSubMethod>
                        <b-row v-if="mode === 'create' ? nameDocSubMethod !== 'RecordID' : true">
                          <b-col cols="4">
                            <label>{{ nameDocSubMethod === "RecordID" ? "Document Submission Method ID" : formatFieldNames(nameDocSubMethod) }}:</label>
                          </b-col>
                          <b-col v-if="editPageViewOnly">
                            <label>{{ AHJ.DocumentSubmissionMethods[i][nameDocSubMethod] }}</label>
                          </b-col>
                          <b-col cols="8" v-else>
                            <label v-if="nameDocSubMethod === 'RecordID'">{{ AHJ.DocumentSubmissionMethods[i][nameDocSubMethod] }}</label>
                            <b-form-select v-else-if="choiceFields.DocumentSubmissionMethod[nameDocSubMethod]" v-model="AHJ.DocumentSubmissionMethods[i][nameDocSubMethod]" :options="choiceFields.DocumentSubmissionMethod[nameDocSubMethod]" />
                            <b-form-input v-else v-model="AHJ.DocumentSubmissionMethods[i][nameDocSubMethod]" type="text" :placeholder="getBFormInputPlaceholder(nameDocSubMethod)" />
                          </b-col>
                        </b-row>
                      </div>
                    </b-tab>
                    <template v-slot:tabs-end>
                      <b-nav-item role="presentation" :disabled="editPageViewOnly" @click.prevent="newTabDocSubMethod" href="#"><b>+</b></b-nav-item>
                    </template>
                  </b-tabs>
                </b-form-group>
              </b-tab>
              <b-tab title="Permit Issue Methods">
                <b-form-group
                      id="input-group-1"
                      label-for="input-1"
                    >
                  <b-tabs card>
                    <b-tab v-for="i in tabsPerIssMethod" :key="'dyn-tab-' + i" :title="'Permit Issue Method ' + getTabTitle('PermitIssueMethods[' + i + ']')">
                      <b-row>
                        <b-col>
                          <b-button size="sm" variant="danger" class="float-right" :disabled="editPageViewOnly" @click="closeTabPerIssMethod(i)">Delete</b-button>
                        </b-col>
                      </b-row>
                      <div v-for="(valuePerIssMethod, namePerIssMethod) in constants.PERMITSUBMISSIONMETHOD_FIELDS" :key=namePerIssMethod>
                        <b-row v-if="mode === 'create' ? namePerIssMethod !== 'RecordID' : true">
                          <b-col cols="4">
                            <label>{{ namePerIssMethod === "RecordID" ? "Permit Issue Method ID" : formatFieldNames(namePerIssMethod) }}:</label>
                          </b-col>
                          <b-col v-if="editPageViewOnly">
                            <label>{{ AHJ.PermitIssueMethods[i][namePerIssMethod] }}</label>
                          </b-col>
                          <b-col cols="8" v-else>
                            <label v-if="namePerIssMethod === 'RecordID'">{{ AHJ.PermitIssueMethods[i][namePerIssMethod] }}</label>
                            <b-form-select v-else-if="choiceFields.PermitIssueMethod[namePerIssMethod]" v-model="AHJ.PermitIssueMethods[i][namePerIssMethod]" :options="choiceFields.PermitIssueMethod[namePerIssMethod]" />
                            <b-form-input v-else v-model="AHJ.PermitIssueMethods[i][namePerIssMethod]" type="text" :placeholder="getBFormInputPlaceholder(namePerIssMethod)" />
                          </b-col>
                        </b-row>
                      </div>
                    </b-tab>
                    <template v-slot:tabs-end>
                      <b-nav-item role="presentation" :disabled="editPageViewOnly" @click.prevent="newTabPerIssMethod" href="#"><b>+</b></b-nav-item>
                    </template>
                  </b-tabs>
                </b-form-group>
              </b-tab>
            </b-tabs>
          <b-button v-if="!editPageViewOnly" class="form-buttons" type="submit" variant="primary">Submit</b-button>
        </b-form>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import axios from "axios";
import constants from "../constants.js";
export default {
  props: [
    'mode',
    'selectedAHJ'
  ],
  data() {
    return {
      constants: constants,
      recordLoading: true,
      editPageViewOnly: true,
      beforeEditAHJRecord: {},
      EditTypeAndRecordTypeAndRecordID: "",
      requestType: "post",
      tabsContact: [],
      tabCounterContact: 0,
      tabsEngReqRev: [],
      tabCounterEngReqRev: 0,
      tabsFeeStructure: [],
      tabCounterFeeStructure: 0,
      tabsAHJInspection: [],
      tabCounterAHJInspection: 0,
      tabsAHJInspectionsContact: [],
      tabsCounterAHJInspectionsContact: [],
      tabsDocSubMethod: [],
      tabCounterDocSubMethod: 0,
      tabsPerIssMethod: [],
      tabCounterPerIssMethod: 0,
      AHJ: {},
      unconfirmedRecordEdits: [],
      choiceFields: constants.CHOICE_FIELDS
    }
  },
  mounted() {
    this.initiateMode();
  },
  methods: {
    initiateMode() {
      if (!this.mode) {
        return;
      } else if (this.mode === 'create') {
        this.AHJ = this.deepCopyObject(constants.AHJ_FIELDS);
      } else if (this.mode === 'update') {
        this.AHJ = this.setAHJFieldsFromResponse(this.selectedAHJ);
        // this.getUnconfirmedRecordEdits();
        this.setTabCounts();
        this.recordLoading = false;
      }
    },
    tryEnterEditPageEditMode() {
      if (this.$store.state.loginStatus.status !== "success") {
        this.$store.commit("setShowLoginModal", true);
        return;
      }
      this.getConfirmedAHJRecord();
      this.editPageViewOnly = false;
    },
    onSubmit() {
      this.editPageViewOnly = true;
      if (this.mode === "create") {
        this.postCreate("AHJ", this.AHJ);
      } else if (this.mode === "update") {
        this.postUpdate("AHJ", this.AHJ, this.AHJ["RecordID"], this.beforeEditAHJRecord);
      }
    },
    onReset() {

    },
    getConfirmedAHJRecord() {
      this.recordLoading = true;
      axios.get(this.$store.state.apiURL + "ahj/" + this.AHJ.RecordID + "/?view=confirmed", {
        headers: {
          Authorization: this.$store.state.loginStatus.authToken
        }
      }).then(response => {
        this.beforeEditAHJRecord = this.setAHJFieldsFromResponse(response.data);
        this.AHJ = this.deepCopyObject(this.beforeEditAHJRecord);
        this.setTabCounts();
        this.recordLoading = false;
      });
    },
    getUnconfirmedRecordEdits() {
      axios.get(this.$store.state.apiURL + "edit/" + "?RecordID__in=" + this.AHJ.RecordID + "&IsConfirmed__in=None", {
        headers: {
          Authorization: this.constants.TOKEN_AUTH
        }
      }).then(response => {
        this.unconfirmedRecordEdits = response.results;
        this.recordLoading = false;
      });
    },
    setTabCounts() {
      this.tabCounterContact = this.AHJ.Contacts.length;
      this.tabsContact = [];
      for (let i = 0; i < this.tabCounterContact; i++) {
        this.tabsContact.push(i);
      }
      this.tabsEngReqRev = [];
      this.tabCounterEngReqRev = this.AHJ.EngineeringReviewRequirements.length;
      for (let i = 0; i < this.tabCounterEngReqRev; i++) {
        this.tabsEngReqRev.push(i);
      }
      this.tabsDocSubMethod = [];
      this.tabCounterDocSubMethod = this.AHJ.DocumentSubmissionMethods.length;
      for (let i = 0; i < this.tabCounterDocSubMethod; i++) {
        this.tabsDocSubMethod.push(i);
      }
      this.tabsPerIssMethod = [];
      this.tabCounterPerIssMethod = this.AHJ.PermitIssueMethods.length;
      for (let i = 0; i < this.tabCounterPerIssMethod; i++) {
        this.tabsPerIssMethod.push(i);
      }
      this.tabCounterAHJInspection = this.AHJ.AHJInspections.length;
      this.tabsAHJInspection = [];
      for (let i = 0; i < this.tabCounterAHJInspection; i++) {
        this.tabsAHJInspection.push(i);
      }
      this.tabsAHJInspectionsContact = [];
      this.tabsCounterAHJInspectionsContact = [];
      for (let ahjInspection of this.AHJ.AHJInspections) {
        this.tabsCounterAHJInspectionsContact.push(ahjInspection.Contacts.length);
        let tabsAHJInspectionContact = [];
        for (let i = 0; i < ahjInspection.Contacts.length; i++) {
          tabsAHJInspectionContact.push(i);
        }
        this.tabsAHJInspectionsContact.push(tabsAHJInspectionContact);
      }
      this.tabCounterFeeStructure = this.AHJ.FeeStructures.length;
      this.tabsFeeStructure = [];
      for (let i = 0; i < this.tabCounterFeeStructure; i++) {
        this.tabsFeeStructure.push(i);
      }
    },
    setAHJFieldsFromResponse(record, parentKey) {
      let result = {};
      let hasSetRecordID = false;
      let recordIDFromEdit = "";
      if (record.hasOwnProperty("EditID")) {
        result["RecordID"] = record["RecordID"];
        result[parentKey] = record["Value"];
        return result;
      } else {
        Object.keys(record).filter(key => key !== "mpoly").forEach(key => { // do not include mpoly for now
          let field = record[key];
          if (field) {
            if (field.hasOwnProperty("Value")) {
              let value = field["Value"];
              if (value && field["RecordID"] === value) {
                hasSetRecordID = true;
                key = "RecordID";
              }
              recordIDFromEdit = field["RecordID"];
              result[key] = value;
            } else if (this.isArray(field)) {
              result[key] = [];
              field.forEach(item => {
                result[key].push(this.setAHJFieldsFromResponse(item, this.getSingularRecordType(key)));
              });
            } else {
              result[key] = this.setAHJFieldsFromResponse(record[key]);
            }
          } else {
            result[key] = field;
          }
        });
        if (!hasSetRecordID && this.isObject(record)) {
          result["RecordID"] = recordIDFromEdit;
        }
        return result;
      }
    },
    postCreate(RecordType, fields, ParentID, ParentRecordType, subRecordID) {
      let createEditObject = {EditType: "create", RecordType: RecordType}
      if (ParentID && ParentRecordType) {
        createEditObject["ParentID"] = ParentID;
        createEditObject["ParentRecordType"] = ParentRecordType;
      }
      if (RecordType === "FeeStructure" && subRecordID) {
        createEditObject["RecordID"] = subRecordID;
      }
      axios.post(this.$store.state.apiURL + "edit/submit/", createEditObject,
        {
          headers: {
            Authorization: this.$store.state.loginStatus.authToken
          }
      }).then(response => {
        let RecordID = response.data["RecordID"];
        fields["RecordID"] = RecordID;
        this.postUpdate(RecordType, fields, RecordID);
      }).catch(error => {
      });
    },
    postUpdate(RecordType, fields, RecordID, beforeEditFields) {
      let updateEditObjects = [];
      Object.keys(fields).forEach(key => {
        let field = fields[key];
        if(field !== null) {
          if (this.isArray(field)) {
            if (this.mode === "update" && beforeEditFields) {
              this.deleteRemovedRecordsInArray(key, field, beforeEditFields);
            }
            for (let i = 0; i < field.length; i++) {
              let subRecordID = field[i]["RecordID"];
              if (subRecordID && (beforeEditFields[key][i] ? subRecordID === beforeEditFields[key][i]["RecordID"] : false)) {
                this.postUpdate(this.getSingularRecordType(key), field[i], subRecordID, beforeEditFields[key][i]);
              } else {
                this.postCreate(this.getSingularRecordType(key), field[i], RecordID, RecordType, subRecordID);
              }
            }
          } else if (this.isObject(field)) {
            let subRecordID = field["RecordID"];
            if (subRecordID) {
              this.postUpdate(key, field, subRecordID, beforeEditFields[key]);
            } else {
              this.postCreate(key, field, RecordID, RecordType);
            }
          } else if(key === "RecordID" || ((this.mode === "create" || !beforeEditFields) ? field === "" : false)
            || (this.mode === "update" && beforeEditFields ? this.checkEditMade(fields, beforeEditFields, key) : false)) {
            return;
          } else {
            let updateEditObject = {EditType: "update", RecordType: RecordType, RecordID: RecordID};
            updateEditObject["FieldName"] = key;
            updateEditObject["Value"] = field;
            updateEditObjects.push(updateEditObject);
          }
        }
      });
      if (updateEditObjects.length > 0) {
        axios.post(this.$store.state.apiURL + "edit/submit/", updateEditObjects,
          {
          headers: {
            Authorization: this.$store.state.loginStatus.authToken
          }
        }).then(response => {
        }).catch(error => {
        });
      }
    },
    deleteRemovedRecordsInArray(key, field, beforeEditFields) {
      let recordsToDelete = beforeEditFields[key].filter(item => {
        let deleted = true;
        for (let i = 0; i < field.length; i++) {
          if (item["RecordID"] === field[i]["RecordID"]) {
            deleted = false;
          }
        }
        return deleted;
      });
      recordsToDelete.forEach(record => this.postDelete(this.getSingularRecordType(key), record["RecordID"]));
    },
    postDelete(RecordType, RecordID) {
      let deleteEditObject = {EditType: "delete", RecordType: RecordType, RecordID: RecordID};
      axios.post(this.$store.state.apiURL + "edit/submit/", deleteEditObject,
        {
        headers: {
          Authorization: this.$store.state.loginStatus.authToken
        }
      }).then(response => {

      }).catch(error => {
      });
    },
    getSingularRecordType(name) {
      return name.slice(0, -1);
    },
    addContact(parent) {
      parent["Contacts"].push(this.deepCopyObject(constants.CONTACT_FIELDS));
    },
    addAddress(parent) {
      parent["Address"] = this.deepCopyObject(constants.ADDRESS_FIELDS);
    },
    addLocation(parent) {
      parent["Location"] = this.deepCopyObject(constants.LOCATION_FIELDS);
    },
    addEngRevReq() {
      this.AHJ.EngineeringReviewRequirements.push(this.deepCopyObject(constants.ENGINEERINGREVIEWREQUIREMENTS_FIELDS));
    },
    addDocSubMethod() {
      this.AHJ.DocumentSubmissionMethods.push(this.deepCopyObject(constants.DOCUMENTSUBMISSIONMETHOD_FIELDS));
    },
    addPerIssMethod() {
      this.AHJ.PermitIssueMethods.push(this.deepCopyObject(constants.PERMITSUBMISSIONMETHOD_FIELDS));
    },
    addFeeStructure() {
      this.AHJ.FeeStructures.push(this.deepCopyObject(constants.FEESTRUCTURE_FIELDS));
    },
    addAHJInspection() {
      this.AHJ.AHJInspections.push(this.deepCopyObject(constants.AHJINSPECTION_FIELDS));
    },
    newTabContact() {
      this.addContact(this.AHJ);
      this.tabsContact.push(this.tabCounterContact++);
    },
    newTabAHJInspectionContact(index) {
      this.addContact(this.AHJ.AHJInspections[index]);
      this.tabsAHJInspectionsContact[index].push(this.tabsCounterAHJInspectionsContact[index]++);
    },
    newTabEngRevReq() {
      this.addEngRevReq();
      this.tabsEngReqRev.push(this.tabCounterEngReqRev++);
    },
    newTabDocSubMethod() {
      this.addDocSubMethod();
      this.tabsDocSubMethod.push(this.tabCounterDocSubMethod++);
    },
    newTabPerIssMethod() {
      this.addPerIssMethod();
      this.tabsPerIssMethod.push(this.tabCounterPerIssMethod++);
    },
    newTabFeeStructure() {
      this.addFeeStructure();
      this.tabsFeeStructure.push(this.tabCounterFeeStructure++);
    },
    newTabAHJInspection() {
      this.addAHJInspection();
      this.tabsAHJInspection.push(this.tabCounterAHJInspection++);
      this.tabsAHJInspectionsContact.push([]);
      this.tabsCounterAHJInspectionsContact.push(0);
    },
    closeTabContact(x) {
      for (let i = 0; i < this.tabsContact.length; i++) {
        if (this.tabsContact[i] === x) {
          this.AHJ.Contacts.splice(i, 1);
          this.tabsContact.splice(i, 1);
        }
        for (let i = 0; i < this.tabsContact.length; i++) {
          this.tabsContact[i] = i;
        }
        this.tabCounterContact = this.tabsContact.length;
      }
    },
    closeTabEngReqReq(x) {
      for (let i = 0; i < this.tabsEngReqRev.length; i++) {
        if (this.tabsEngReqRev[i] === x) {
          this.AHJ.EngineeringReviewRequirements.splice(i, 1);
          this.tabsEngReqRev.splice(i, 1);
        }
        for (let i = 0; i < this.tabsEngReqRev.length; i++) {
          this.tabsEngReqRev[i] = i;
        }
        this.tabCounterEngReqRev = this.tabsEngReqRev.length;
      }
    },
    closeTabDocSubMethod(x) {
      for (let i = 0; i < this.tabsDocSubMethod.length; i++) {
        if (this.tabsDocSubMethod[i] === x) {
          this.AHJ.DocumentSubmissionMethods.splice(i, 1);
          this.tabsDocSubMethod.splice(i, 1);
        }
        for (let i = 0; i < this.tabsDocSubMethod.length; i++) {
          this.tabsDocSubMethod[i] = i;
        }
        this.tabCounterDocSubMethod = this.tabsDocSubMethod.length;
      }
    },
    closeTabPerIssMethod(x) {
      for (let i = 0; i < this.tabsPerIssMethod.length; i++) {
        if (this.tabsPerIssMethod[i] === x) {
          this.AHJ.PermitIssueMethods.splice(i, 1);
          this.tabsPerIssMethod.splice(i, 1);
        }
        for (let i = 0; i < this.tabsPerIssMethod.length; i++) {
          this.tabsPerIssMethod[i] = i;
        }
        this.tabCounterPerIssMethod = this.tabsPerIssMethod.length;
      }
    },
    closeTabFeeStructure(x) {
      for (let i = 0; i < this.tabsFeeStructure.length; i++) {
        if (this.tabsFeeStructure[i] === x) {
          this.AHJ.FeeStructures.splice(i, 1);
          this.tabsFeeStructure.splice(i, 1);
        }
        for (let i = 0; i < this.tabsFeeStructure.length; i++) {
          this.tabsFeeStructure[i] = i;
        }
        this.tabCounterFeeStructure = this.tabsFeeStructure.length;
      }
    },
    closeTabAHJInspection(x) {
      for (let i = 0; i < this.tabsAHJInspection.length; i++) {
        if (this.tabsAHJInspection[i] === x) {
          this.AHJ.AHJInspections.splice(i, 1);
          this.tabsAHJInspection.splice(i, 1);
          this.tabsCounterAHJInspectionsContact.splice(i, 1);
          this.tabsAHJInspectionsContact.splice(i, 1);
        }
        for (let i = 0; i < this.tabsAHJInspection.length; i++) {
          this.tabsAHJInspection[i] = i;
        }
        this.tabCounterAHJInspection = this.tabsAHJInspection.length;
      }
    },
    closeTabAHJInspectionContact(index, x) {
      for (let i = 0; i < this.tabsAHJInspectionsContact[index].length; i++) {
        if (this.tabsAHJInspectionsContact[index][i] === x) {
          this.AHJ.AHJInspections[index].Contacts.splice(i, 1);
          this.tabsAHJInspectionsContact[index].splice(i, 1);
        }
        for (let i = 0; i < this.tabsAHJInspectionsContact[index].length; i++) {
          this.tabsAHJInspectionsContact[index][i] = i;
        }
        this.tabsCounterAHJInspectionsContact[index] = this.tabsAHJInspectionsContact[index].length;
      }
    },
    deepCopyObject(objectToCopy) {
      let result = {};
      Object.keys(objectToCopy).forEach(key => {
        let field = objectToCopy[key];
        if (field) {
          if (this.isArray(field)) {
            result[key] = [];
            field.forEach(item => {
              result[key].push(this.deepCopyObject(item));
            });
          } else if(this.isObject(field)) {
            result[key] = this.deepCopyObject(field);
          } else {
            result[key] = field;
          }
        } else {
          result[key] = field;
        }
      });
      return result;
    },
    checkEditMade(before, after, field) {
      return before[field] === after[field];
    },
    isArray(item) {
      return item.constructor === Array;
    },
    isObject(item) {
      return typeof item === "object" && item !== null;
    },
    getBFormInputPlaceholder(fieldName) {
      return "Enter a " + this.formatFieldNames(fieldName) + "...";
    },
    getTabTitle(type) {
      type += ".RecordID";
      let RecordID = type.split(/[\[\].]/).filter(i => i !== "").reduce((o, i) => {
        if (!o || !o[i]) {
          return undefined;
        } else {
          return o[i];
        }
      }, this.AHJ);
      if (RecordID) {
        return RecordID;
      }
      return "(new)";
    },
    formatFieldNames(name) {
      let result = "";
      let index = 0;
      while (name[index] >= 65 && name[index] <= 90) {
        index++;
      }
      index--;
      result += name.substring(0, index);
      if (name.substring(0, 3) === "AHJ") {
        result += "AHJ ";
        name = name.substring(3);
      }
      for (let i = index; i < name.length; i++) {
        if (/([^A-Za-z0-9\.\$]+)|([A-Z])(?=[A-Z][a-z])|([A-Za-z])(?=\$?[0-9]+(?:\.[0-9]+)?)|([0-9])(?=[^\.0-9])|([a-z])(?=[A-Z])/.test(name.substring(index, i))) {
          result += name.substring(index, i - 1) + " ";
          index = i - 1;
        }
      }
      result += name.substring(index, name.length);
      return result;
    }
  },
  computed: {
    modes() {
      if(this.$store.state.loginStatus["isSuper"]) {
        return [
          { value: "update", text: "Edit an existing AHJ..." },
          { value: "create", text: "Submit a new AHJ..." }
        ];
      } else {
        return [
          { value: "update", text: "Edit an existing AHJ..." }
        ];
      }
    }
  }
};
</script>

<style scoped>

.form-buttons {
  float: right;
}

</style>
