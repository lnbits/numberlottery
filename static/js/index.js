const mapGame = obj => {
  obj._data = _.clone(obj)
  obj.closing_date = Quasar.date.formatDate(
    new Date(obj.closing_date),
    'YYYY-MM-DD HH:mm'
  )
  return obj
}

window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  data() {
    return {
      games: [],
      players: {
        show: false,
        data: []
      },
      numbersTable: {
        columns: [
          {name: 'id', align: 'left', label: 'ID', field: 'id'},
          {name: 'name', align: 'left', label: 'Name', field: 'name'},
          {
            name: 'closing_date',
            align: 'right',
            label: 'Closing Date',
            field: 'closing_date'
          },
          {
            name: 'buy_in_max',
            align: 'left',
            label: 'buy_in_max',
            field: 'buy_in_max'
          },
          {
            name: 'odds',
            align: 'left',
            label: 'odds',
            field: 'odds'
          },
          {
            name: 'haircut',
            align: 'left',
            label: 'haircut',
            field: 'haircut'
          },
          {
            name: 'completed',
            align: 'left',
            label: 'completed',
            field: 'completed'
          }
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      playersTable: {
        columns: [
          {name: 'id', align: 'left', label: 'ID', field: 'id'},
          {
            name: 'ln_address',
            align: 'left',
            label: 'LN Address',
            field: 'ln_address'
          },
          {name: 'buy_in', align: 'left', label: 'Buy in', field: 'buy_in'},
          {
            name: 'block_number',
            align: 'left',
            label: 'Number',
            field: 'block_number'
          },
          {name: 'owed', align: 'left', label: 'Owed', field: 'owed'},
          {name: 'paid', align: 'left', label: 'Paid', field: 'paid'}
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      formDialogNumbers: {
        show: false,
        fixedAmount: true,
        data: {
          name: '',
          number_of_players: 2,
          buy_in: 1000,
          wallet: null,
          mempool: 'https://mempool.space'
        }
      }
    }
  },
  methods: {
    async getGames() {
      await LNbits.api
        .request(
          'GET',
          '/numberlottery/api/v1',
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          if (response.data != null) {
            console.log(response.data)
            for (const game of response.data) {
              this.games.push(mapGame(game))
            }
          }
        })
        .catch(err => {
          LNbits.utils.notifyApiError(err)
        })
    },
    async openPlayers(game_id) {
      await LNbits.api
        .request(
          'GET',
          '/numberlottery/api/v1/players/' + game_id,
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          if (response.data != null) {
            this.players.data = response.data
          }
        })
        .finally(() => {
          this.players.show = true
        })
        .catch(err => {
          LNbits.utils.notifyApiError(err)
        })
    },
    async createGame() {
      const date = new Date(this.formDialogNumbers.data.closing_date)
      const unixTimestamp = Math.floor(date.getTime() / 1000)
      const data = {
        name: this.formDialogNumbers.data.name,
        buy_in_max: this.formDialogNumbers.data.buy_in_max,
        odds: this.formDialogNumbers.data.odds,
        closing_date: parseInt(unixTimestamp),
        haircut: this.formDialogNumbers.data.haircut
      }
      const wallet = _.findWhere(this.g.user.wallets, {
        id: this.formDialogNumbers.data.wallet
      })
      try {
        const response = await LNbits.api.request(
          'POST',
          '/numberlottery/api/v1',
          wallet.adminkey,
          data
        )
        if (response.data) {
          console.log(response.data)
          this.games.push(mapGame(response.data))
          this.formDialogNumbers.show = false
        }
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },
    deleteGame(game_id) {
      const game = _.findWhere(this.games, {id: game_id})

      LNbits.utils
        .confirmDialog('Are you sure you want to delete this numbers?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              '/numberlottery/api/v1/' + game_id,
              _.findWhere(this.g.user.wallets, {id: game.wallet}).adminkey
            )
            .then(response => {
              this.games = _.reject(this.games, obj => obj.id === game_id)
            })
            .catch(err => {
              LNbits.utils.notifyApiError(err)
            })
        })
    },
    exportCSV() {
      LNbits.utils.exportCSV(this.numbersTable.columns, this.games)
    }
  },
  async mounted() {
    // CHECK COINFLIP SETTINGS
    await this.getGames()
  }
})
