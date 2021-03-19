
import React from 'react'
import { Form, Col, Row, Card, CardGroup, Button, Alert, Spinner, Table} from 'react-bootstrap'
import axios from 'axios'

export default class Leaders extends React.Component {
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

        
        console.log(this.state.p)

        

    }

    async componentDidMount() {
        
        await axios.post('/win-calculator')
            .then(response => {
                this.setState({ p : JSON.stringify(response.data)})
            })

        console.log(this.state.p)

    }

    

    render() {


        return (


            <div>

                <p>{this.state.p}</p>
                <Button onClick={this.test}></Button>
                   
            </div>
         


        );
    };
}

