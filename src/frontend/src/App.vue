<template>
  <div>
    <section class="hero container">
      <b-image v-if="imagePath" :src="imagePath" class="container hero-image"></b-image>
      <div :class="{ 'hero-offset': imagePath, 'hero-text': true }">Network Search</div>
    </section>

    <section class="container">
      <div class="form columns">
        <div class="column is-half">
          <!-- Column Selector -->
          <b-dropdown v-model="selectedColumns" multiple aria-role="list">
            <template #trigger>
              <b-button type="is-danger" icon-right="menu-down">Columns</b-button>
            </template>
            <div v-for="column of columns" :key="column.field">
              <b-dropdown-item class="dropdown-item" :value="column" aria-role="listitem">
                <span>{{ column.label }}</span>
              </b-dropdown-item>
            </div>
          </b-dropdown>

          <!-- Datacenter Selector -->
          <b-dropdown v-model="selectedDatacenters" multiple aria-role="list">
            <template #trigger>
              <b-button
                type="is-primary"
                icon-right="menu-down"
              >Datacenters ({{ selectedDatacenters.length }})</b-button>
            </template>
            <div v-for="datacenter of datacenters" :key="datacenter">
              <b-dropdown-item class="dropdown-item" :value="datacenter" aria-role="listitem">
                <span>{{ datacenter }}</span>
              </b-dropdown-item>
            </div>
          </b-dropdown>

          <b-switch v-model="allDatacenters" class="all-dcs">All Datacenters</b-switch>
        </div>
        <div class="column is-half export-button">
          <b-dropdown aria-role="list">
            <template #trigger>
              <b-button
                type="is-primary"
                icon-left="database-export"
                icon-right="menu-down"
                class="has-background-success"
              >Export</b-button>
            </template>
            <b-dropdown-item aria-role="listitem" v-on:click="exportData('json')">
              <div class="media">
                <b-icon class="media-left" icon="code-json" type="is-black"></b-icon>
                <div class="media-content">
                  <h3>JSON</h3>
                  <small>Export as JSON</small>
                </div>
              </div>
            </b-dropdown-item>
            <b-dropdown-item aria-role="listitem" v-on:click="exportData('csv')">
              <div class="media">
                <b-icon class="media-left" icon="file-delimited" type="is-black"></b-icon>
                <div class="media-content">
                  <h3>CSV</h3>
                  <small>Export as CSV</small>
                </div>
              </div>
            </b-dropdown-item>
          </b-dropdown>
        </div>
      </div>
      <div>
        <b-input :placeholder="searchPlaceholder" v-model="search" icon="magnify" size="is-medium"></b-input>
      </div>
    </section>

    <section class="container">
      <b-table
        class="data-table"
        :data="filteredNetworks"
        :columns="orderedColumns"
        default-sort="datacenter"
        default-sort-direction="asc"
        striped
        paginated
        per-page="50"
      ></b-table>
    </section>
  </div>
</template>

<script>
import axios from "axios";
import Papa from 'papaparse'
import { isInSubnet } from "is-in-subnet";

const ipRegexp =
  /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

export default {
  name: "App",
  data: () => ({
    search: "",
    networks: [],
    selectedDatacenters: [],
    selectedColumns: [],
    allDatacenters: true,
    imagePath: process.env.VUE_APP_IMG_URL,
    columns: [
      { order: 1, label: "Network ID", field: "id", sortable: true },
      {
        order: 2,
        label: "Data Center",
        field: "datacenter",
        visible: true,
        sortable: true,
      },
      { order: 3, label: "VLAN", field: "vlan", visible: true, sortable: true },
      {
        order: 4,
        label: "Network",
        field: "network",
        visible: true,
        sortable: true,
      },
      {
        order: 5,
        label: "Description",
        field: "description",
        visible: true,
        sortable: true,
      },
      { order: 6, label: "Netmask", field: "netmask", sortable: true },
      { order: 7, label: "Bitmask", field: "bitmask", sortable: true },
      {
        order: 8,
        label: "Gateway",
        field: "gateway",
        visible: true,
        sortable: true,
      },
      {
        order: 9,
        label: "Network Address",
        field: "network_address",
        sortable: true,
      },
      {
        order: 10,
        label: "Broadcast Address",
        field: "broadcast_address",
        sortable: true,
      },
      {
        order: 11,
        label: "First IP",
        field: "first_usable_ip",
        sortable: true,
      },
      { order: 12, label: "Last IP", field: "last_usable_ip", sortable: true },
      {
        order: 13,
        label: "Origin Device",
        field: "origin_device",
        visible: true,
        sortable: true,
      },
    ],
  }),
  watch: {
    allDatacenters(state) {
      if (!state) {
        this.selectedDatacenters = [];
      } else {
        this.selectedDatacenters = this.datacenters;
      }
    },
    selectedDatacenters(state) {
      if (state.length !== this.datacenters.length) {
        this.allDatacenters = false;
      }
    },
  },
  computed: {
    searchPlaceholder() {
      return `Search ${this.networks.length} networks...`
    },
    filteredColumns() {
      return this.columns.filter((column) => column.visible);
    },
    orderedColumns() {
      const result = [...this.selectedColumns];
      result.sort((a, b) => {
        if (a.order > b.order) return 1;
        else if (a.order < b.order) return -1;
        return 0;
      });
      return result;
    },
    datacenters() {
      const datacenters = new Set();
      this.networks.map((network) => datacenters.add(network.datacenter));
      return Array.from(datacenters).sort();
    },
    filteredNetworks() {
      let result = this.networks.filter((network) =>
        this.selectedDatacenters.includes(network.datacenter)
      );

      if (this.search) {
        let isIpSearch = false;
        if (ipRegexp.test(this.search)) {
          isIpSearch = true;
        }
        result = result.filter((network) => {
          if (isIpSearch && network.network) {
            if (isInSubnet(this.search, network.network)) {
              return true;
            }
          } else {
            for (let value of Object.values(network)) {
              if (
                value &&
                value
                  .toString()
                  .toLowerCase()
                  .includes(this.search.toLowerCase())
              )
                return true;
            }
            return false;
          }
        });
      }

      return result;
    },
  },
  methods: {
    async getNetworks() {
      const { data: res } = await axios.get(
        `${process.env.VUE_APP_API_BASE || "http://localhost:8000"}/v1/networks`
      );
      this.networks = res;
      this.selectedDatacenters = this.datacenters;
      this.selectedColumns = this.filteredColumns;
    },
    exportData(dataType) {
      let blob
      switch (dataType) {
        case 'json':
          blob = new Blob([JSON.stringify(this.filteredNetworks, null, 4)], { type: 'text/json;charset=utf-8' })
          break
        case 'csv':
          blob = new Blob([Papa.unparse(this.filteredNetworks)], { type: 'text/csv;charset=utf-8' })
          break
      }
      const urlBlob = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = urlBlob
      anchor.target = "_blank"
      anchor.download = `network-export-${new Date().toJSON()}.${dataType === 'json' ? 'json' : 'csv'}`
      anchor.click()
      URL.revokeObjectURL(urlBlob)
    },
  },
  mounted() {
    this.getNetworks();
  },
};
</script>

<style lang="scss" scoped>
@import url("https://fonts.googleapis.com/css2?family=Roboto&display=swap");

.hero-image {
  width: 65%;
  padding: 20px;
  padding-bottom: 50px;
}

.hero-text {
  text-align: center;
  color: #fff;
  font-family: "Roboto";
  font-size: 3rem;
  font-weight: bold;
  letter-spacing: 0.22rem;
  padding-bottom: 2rem;
}

.hero-offset {
  margin-top: -3rem;
}

.form {
  padding-left: 10px;
}

.data-table {
  padding-top: 20px;
}

.all-dcs {
  margin-top: 8px;
  padding-left: 16px;
  color: #fff;
}

.export-button {
  display: flex;
  justify-content: end;
}
</style>
