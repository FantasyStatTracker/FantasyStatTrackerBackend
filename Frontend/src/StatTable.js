
import React from 'react'
import {  Card, CardGroup, Button, Table, ButtonGroup } from 'react-bootstrap'
import axios from 'axios'

export default class StatTable extends React.Component {
    constructor(props) {
        super(props);

        this.state = {

            p: "",
            dataArray: [],
            Players: [],
            Categories: [],
            AllData: [],
            Leaders: [],
            f: [],
            show: false,
            Winning: [],
            showWinning: false,
            LeaderPlayer: [],
            Available: false,
            AllLeader: []

        };


        this.test = this.test.bind(this)
        this.getLeaders = this.getLeaders.bind(this)
        this.computeLeaders = this.computeLeaders.bind(this)
        this.winningMatchup = this.winningMatchup.bind(this)
    }


    async computeLeaders() {
        var bodyFormData = new FormData();
        bodyFormData.append("data", JSON.stringify(this.state.AllData))
        await axios.post('https://react-flask-fantasy.herokuapp.com/win-calculator', bodyFormData)

            .then((response) => {
                this.setState({ Leaders: JSON.stringify(response.data) })
            })

        var arr = []
        var cat = []
        var obj = JSON.parse(this.state.Leaders)
        
        for (var i in obj) {
            cat.push(i)
            arr.push(obj[i])
        }

        await this.setState({AllLeader : arr})
        await this.setState({Categories: cat})
        await this.setState({show: true})
        await this.setState({ showWinning: false })



    }

    test() {

        var arr = []
        var obj = JSON.parse(this.state.p)
        var g = Object.keys(obj)

        var catArray = []

        for (var i in g) {
            var w = {}
            w[g[i]] = obj[g[i]]
            arr.push(w)
        }

        this.setState({ AllData: arr })
        for (var x in (arr[0][g[0]])) {
            catArray.push(x)
        }
        this.setState({ Players: g })
        this.setState({ dataArray: arr })
        this.setState({ Categories: catArray })

        this.setState({Available: true})
        this.setState({show: false})
        this.setState({ showWinning: false })



    }

    async componentDidMount() {

        await axios.get('https://react-flask-fantasy.herokuapp.com/test')
            .then(response => {
                this.setState({ p: JSON.stringify(response.data) })
            })


    }

    async getLeaders() {
        var bodyFormData = new FormData();
        bodyFormData.append("data", JSON.stringify(this.state.AllData))

        await axios.post('https://react-flask-fantasy.herokuapp.com/win-calculator', bodyFormData)

            .then((response) => {
                this.setState({ Leaders: JSON.stringify(response.data) })
            })



    }

    async winningMatchup() {
        var bodyFormData = new FormData();
        bodyFormData.append("data", JSON.stringify(this.state.AllData))

        await axios.post('https://react-flask-fantasy.herokuapp.com/winning-matchups', bodyFormData)

            .then((response) => {

                this.setState({ Winning: JSON.stringify(response.data) })
            })


        var arr = []
        var obj = JSON.parse(this.state.Winning)
        var g = Object.keys(obj)

        for (var i in g) {
            var x = {}
            x[g[i]] = obj[g[i]]
            arr.push(x)
        }

        await this.setState({ Winning: arr })
        await this.setState({ LeaderPlayer: g })
        await this.setState({ showWinning: true })
        await this.setState({show: false})



    }


    render() {


        return (


            <div>


                <Button onClick={this.test}>View Updated Current Week Stats and Leaders</Button>
                <CardGroup>
                    {this.state.dataArray.map((item, i) => {
                        return (
                            <Card style={{ width: '18rem' }}>
                                <Card.Body>

                                    <Card.Title
                                        adjustsFrontSizeToFit
                                        style={{ textAlign: 'center', fontSize: '1rem' }}>
                                        {this.state.Players[i]}
                                    </Card.Title>
                                    <Card.Text
                                        adjustsFrontSizeToFit
                                        style={{ textAlign: 'center', fontSize: '1rem' }}>
                                        <Table responsive size="sm">

                                            <tbody>
                                                {this.state.Categories.map((cat, x) =>
                                                    <tr>
                                                        <td>
                                                            {cat}
                                                        </td>

                                                        <td>
                                                            {item[this.state.Players[i]][cat]}
                                                        </td>

                                                    </tr>
                                                )}
                                            </tbody>
                                        </Table>
                                    </Card.Text>
                                </Card.Body>
                            </Card>

                        )


                    })
                    }
                </CardGroup>

                {
                    this.state.Available === false ?
                    <p></p>
                    :
                    <ButtonGroup>
                    <Button onClick={this.computeLeaders}>Week Category Leaders</Button>
                    <Button onClick={this.winningMatchup}>Show that Aaron is Winner</Button>
                    </ButtonGroup>
                }
                



                {
                    this.state.show === false ?

                        <p></p>

                        :

                        <div>
                            <CardGroup>
                            {
                                this.state.AllLeader.map((item, i) => {
                                    return (
                                        <Card>
                                            <Table>
                                                <div>
                                                    <thead>
                                                        <tr>
                                    {this.state.Categories[i]}
                                  
                                    </tr>
                                    </thead>
                                    <tbody>
                                    
                                    
                                    {item.map((val, x) => {
                                        return (
                                        <tr>
                                            <td>
                                        {val[0]}
                                        </td>
                                        <td>
                                            {val[1]}
                                        </td>
                                        </tr>
                                        )
                                    })}

                                    </tbody>

                                    </div>
                                    </Table>
                                    </Card>
                                    )
                                })}
                                </CardGroup>
                                </div>


                            }

                              

                


                
                    {
                        this.state.showWinning === false ?
                        <p></p>

                        :

                        <div>

                            <Table>
                                {this.state.Winning.map((item, i) => {
                                    return (
                                        <div>

                                            <thead>
                                                <tr>{this.state.LeaderPlayer[i]} : {item[this.state.LeaderPlayer[i]].length} Teams</tr>
                                            </thead>
                                            <tbody>
                                            {item[this.state.LeaderPlayer[i]].length === 0 ? <th><strong>LOL</strong></th> : null}
                                                <tr>
                                                    
                                                    
                                                    {item[this.state.LeaderPlayer[i]].map((x, e) => {
                                                        return (<th>{x}</th>)
                                                        
                                                        
                                                    })
                                                    }
                                                
                                                
                                                </tr>
                                            </tbody>

                                        </div>

                                    )
                                })}
                            </Table>

                        </div>


                }







            </div>



        );
    };
}

