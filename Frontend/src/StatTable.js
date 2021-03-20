
import React from 'react'
import {  Card, CardGroup, Button, Table, ButtonGroup, Nav, Navbar, Form, FormControl, ToggleButton} from 'react-bootstrap'
import axios from 'axios'
import "./PageStyle.css"

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
            AccessBoolean: [true,false,false],
            AllLeader: []

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

        await this.setState({AllLeader : arr})
        await this.setState({Categories: cat})

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
        var g = Object.keys(obj)

        for (var i in g) {
            var x = {}
            x[g[i]] = obj[g[i]]
            arr.push(x)
        }

        await this.setState({ Winning: arr })
        await this.setState({ LeaderPlayer: g })

        this.showContent(e)

    }

    async showContent(e) {
        var arr = []
        for (var i = 0; i < this.state.AccessBoolean.length; i++) {
            arr.push(false)
        }
        var value = parseInt(e.target.id)
        arr[value] = true

        await this.setState({AccessBoolean: arr})

        

        
    }


    render() {


        return (


            <div>
                <>
  <Navbar bg="dark" variant="dark">
    <Navbar.Brand href="#home">Fantasy Stat Track</Navbar.Brand>
    <Nav className="mr-auto">
      <Button variant="dark" id="0" onClick={this.showContent}>Home</Button>
      <Button variant="dark" id="1" onClick={this.computeLeaders}>Leaders</Button>
      <Button variant="dark" id ="2" onClick={this.winningMatchup}>Team vs Other Teams</Button>
    </Nav>
    <Form inline>
      <FormControl type="text" placeholder="Search" className="mr-sm-2" />
      <Button variant="outline-info">Search</Button>
    </Form>
  </Navbar>
  
</>
<br/>

{this.state.AccessBoolean[0] === false ?
    <p>
    </p>

    :

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

                }
                

        



                {
                    this.state.AccessBoolean[1] === false ?

                        <p></p>

                        :

                        <div>
                            <h1>Current Week Category Ranks</h1>
                            <CardGroup>
                            
                            {
                                this.state.AllLeader.map((item, i) => {
                                    return (
                                        <Card>
                                            <Table className="CategoryRank" responsive>
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
                        this.state.AccessBoolean[2] === false ?
                        <p></p>

                        :

                        <div>

                            <Table>
                                <h1>Wins if everyone played everyone</h1>
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

