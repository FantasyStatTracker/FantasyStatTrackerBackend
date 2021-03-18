
import './App.css';
import React from 'react'
import StatTable from './StatTable.js'
import Leaders from './Leaders.js'
import 'bootstrap/dist/css/bootstrap.min.css';

class App extends React.Component {
  state = {
    isLoading: true
  }


  render() {
    const {Categories, isLoading} = this.state;

    return (
      <div id="Container">
            <StatTable></StatTable>
            
            
      </div>
    )
  }

}

export default App;