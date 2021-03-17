
import React from 'react'
import { Form, Col, Row, Card, CardGroup, Button, Alert, Spinner, Table} from 'react-bootstrap'
import axios from 'axios'

export default class Test extends React.Component {
    constructor(props) {
        super(props);

        this.state = {

            p: "",
            dataArray: [],
            Players: [],
            Categories: []
   
        };


        this.test = this.test.bind(this)
    }


   test() {

        var arr = []
        var obj = JSON.parse(this.state.p)
        var g = Object.keys(obj)
        console.log(g)

        var catArray = []
        
        for (var i in g) {
            var w = {}
            w[g[i]] = obj[g[i]]
            arr.push(w)
        }

        console.log(arr)
        for (var x in (arr[0][g[0]])) {
            catArray.push(x)
        }
        console.log(catArray)
        this.setState({Players: g})
        this.setState({dataArray: arr})
        this.setState({Categories: catArray})

        {arr.map((item, i) => {
            console.log(g[i])
            console.log(item[g[i]].AST)

            })
        }

    }

    async componentDidMount() {
        
        await axios.get('/test')
            .then(response => {
                this.setState({ p : JSON.stringify(response.data)})
            })

        console.log(this.state.p)

    }

    

    render() {


        return (


            <div>

                <Button onClick={this.test}>View Updated Current Week Stats and Leaders</Button>
               <CardGroup>
                {this.state.dataArray.map((item, i) => {
                return (
                    <Card style={{width: '18rem'}}>
                        <Card.Body>
                    
                     <Card.Title
                     adjustsFrontSizeToFit
                     style={{textAlign:'center', fontSize:'1rem'}}>
                    {this.state.Players[i]} 
                    </Card.Title>
                    <Card.Text
                    adjustsFrontSizeToFit
                    style={{textAlign:'center', fontSize:'1rem'}}>
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
            
                
                
                   
            </div>
         


        );
    };
}

