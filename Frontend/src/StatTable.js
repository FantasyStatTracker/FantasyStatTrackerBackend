
import React from 'react'
import { Card, CardGroup, Container, Button, Table, ButtonGroup, Nav, Navbar, Form, FormControl, ToggleButton, Col, Row, Badge, Alert, DropdownButton, Dropdown } from 'react-bootstrap'
import axios from 'axios'
import "./PageStyle.css"
import DropdownMenu from 'react-bootstrap/esm/DropdownMenu';

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

            Winning: [],

            LeaderPlayer: [],
            AccessBoolean: [true, false, false],
            AllLeader: [],
            keys: []

        };


        this.getLeaders = this.getLeaders.bind(this)
        this.computeLeaders = this.computeLeaders.bind(this)
        this.winningMatchup = this.winningMatchup.bind(this)
        this.showContent = this.showContent.bind(this)
    }


    async computeLeaders(e) {
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

        await this.setState({ AllLeader: arr })
        await this.setState({ Categories: cat })

        this.showContent(e)



    }


    async componentDidMount() {

        await axios.get('https://react-flask-fantasy.herokuapp.com/test')
            .then(response => {
                this.setState({ p: JSON.stringify(response.data) })
            })

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


    }

    async getLeaders() {
        var bodyFormData = new FormData();
        bodyFormData.append("data", JSON.stringify(this.state.AllData))

        await axios.post('https://react-flask-fantasy.herokuapp.com/win-calculator', bodyFormData)

            .then((response) => {
                this.setState({ Leaders: JSON.stringify(response.data) })
            })



    }

    async winningMatchup(e) {
        var bodyFormData = new FormData();
        bodyFormData.append("data", JSON.stringify(this.state.AllData))

        await axios.post('https://react-flask-fantasy.herokuapp.com/winning-matchups', bodyFormData)

            .then((response) => {

                this.setState({ Winning: JSON.stringify(response.data) })
            })


        var arr = []
        var obj = JSON.parse(this.state.Winning)
        var PlayerList = Object.keys(obj)


        for (var i in PlayerList) {
            var x = {}
            console.log(obj[PlayerList[i]])

            x[PlayerList[i]] = obj[PlayerList[i]]
            arr.push(x)
        }

        await this.setState({ Winning: arr })
        await this.setState({ LeaderPlayer: PlayerList })

        console.log(arr)



        {
            this.state.Winning.map((item, i) => {

                console.log(this.state.LeaderPlayer[i])

                {
                    item[this.state.LeaderPlayer[i]].map((x, e) => {
                        console.log(Object.keys(x)[0])
                        {
                            (x[Object.keys(x)].map((r, w) => {
                                console.log(r)
                            }))
                        }


                    })
                }



            })
        }


        this.showContent(e)

    }

    async showContent(e) {
        var arr = []
        for (var i = 0; i < this.state.AccessBoolean.length; i++) {
            arr.push(false)
        }
        var value = parseInt(e.target.id)
        arr[value] = true

        await this.setState({ AccessBoolean: arr })

        /*
                
                */



    }


    render() {


        return (


            <div>
                <>
                    <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
                        <Navbar.Toggle aria-controls="responsive-navbar-nav" />
                        <Navbar.Collapse id="responsive-navbar-nav">
                            <Navbar.Brand>Fantasy Stat Track</Navbar.Brand>
                            <Nav className="mr-auto">
                                <Button variant="dark" id="0" onClick={this.showContent}>Home</Button>
                                <Button variant="dark" id="1" onClick={this.computeLeaders}>Leaders</Button>
                                <Button variant="dark" id="2" onClick={this.winningMatchup}>Team vs Other Teams</Button>
                            </Nav>

                        </Navbar.Collapse>
                    </Navbar>

                </>
                <br />

            <Container fluid>
                <Col>
                <Row>
                {this.state.AccessBoolean[0] === false ?
                    <p>
                    </p>

                    :
                    <Container fluid>

                        <h1 style={{ textAlign: 'center' }}>Current Week Stats by Team</h1>
                        <Table className="StatTable" responsive>
                            {this.state.dataArray.map((item, i) => {
                                return (

                                    <Table bordered >
                                        <td><strong>{this.state.Players[i]}</strong></td>

                                        {this.state.Categories.map((cat, x) =>
                                            <td>
                                                <strong>{cat}</strong>
                                            </td>
                                        )}
                                        <tbody>

                                            <tr>


                                                <td></td>
                                                {this.state.Categories.map((cat, x) =>



                                                    <td>
                                                        {item[this.state.Players[i]][cat]}
                                                    </td>

                                                )}


                                            </tr>


                                        </tbody>
                                    </Table>


                                )


                            })
                            }

                        </Table>
                        </Container>

                }






                {
                    this.state.AccessBoolean[1] === false ?

                        <p></p>

                        :
                        <div >




                            <h1 style={{ textAlign: 'center' }}>Current Week Category Ranks</h1>
                            <div className="tableContent">


                                <Table className="InnerTable" style={{ width: '100%' }}>
                                    <CardGroup>
                                        {
                                            this.state.AllLeader.map((item, i) => {

                                                return (

                                                    <Card>
                                                        <Table style={{ width: '100%' }}>



                                                            <thead>
                                                                <th style={{ fontSize: '1.3rem' }}>

                                                                    {this.state.Categories[i]} Standings


                                                        </th>
                                                            </thead>
                                                            <tbody>

                                                                <tr>
                                                                    {item.map((val, x) => {
                                                                        return (

                                                                            <p>
                                                                                { x === 0 ?
                                                                                    <div>
                                                                                        <td><strong>{val[0]}</strong></td>
                                                                                        <td>
                                                                                            <strong>{val[1]}</strong>
                                                                                        </td>
                                                                                    </div>

                                                                                    :
                                                                                    <div>
                                                                                        <td>{val[0]}</td>
                                                                                        <td className="Value">
                                                                                            {val[1]}
                                                                                        </td>
                                                                                    </div>
                                                                                }

                                                                            </p>

                                                                        )
                                                                    })}

                                                                </tr>

                                                            </tbody>




                                                        </Table>
                                                    </Card>


                                                )

                                            })}
                                    </CardGroup>
                                </Table>



                            </div>



                        </div>


                }







                {
                    this.state.AccessBoolean[2] === false ?
                        <p></p>

                        :

                        <div>

                            <h1 style={{ textAlign: 'center' }}>Is your Team Bad?</h1>
                            <Table bordered responsive className="OtherTeamTable">
                                {this.state.Winning.map((item, i) => {
                                    return (
                                        <div>


                                            <Badge className="OtherTeam" variant="secondary" style={{ fontSize: '1.2rem' }}>{this.state.LeaderPlayer[i]} : {item[this.state.LeaderPlayer[i]].length} Teams</Badge>


                                            <tbody>
                                                {item[this.state.LeaderPlayer[i]].length === 0 ? <Alert variant="danger" style={{ fontSize: '2.2rem' }}>Your Team is Bad</Alert> : null}
                                                <tr>



                                                    {item[this.state.LeaderPlayer[i]].map((x, e) => {

                                                        return (
                                                            
                                                            <td>
                                                            <Dropdown>
                                                                <Dropdown.Toggle variant="secondary">{Object.keys(x)[0]} : {x[Object.keys(x)].length}</Dropdown.Toggle>

                                                            
                                                            <Dropdown.Menu>
                                                                {x[Object.keys(x)].map((categoryWon, w) => {
                                                                    return (
                                                                        <Dropdown.Item>{categoryWon}</Dropdown.Item>
                                                                    )
                                                                })}
                                                                </Dropdown.Menu>


                                                            </Dropdown>
                                                            </td>
                                                            
                                                        )


                                                    })
                                                    }
                                                   


                                                </tr>
                                                <br />
                                            </tbody>

                                        </div>

                                    )
                                })}
                            </Table>

                        </div>


                }
                </Row>
</Col>
</Container>





            </div>



        );
    };
}

