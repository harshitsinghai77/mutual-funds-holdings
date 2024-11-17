import { Grommet } from 'grommet'
import { theme } from './theme'

import Dashboard from './components/dashboard';

function App() {
  return (
    <Grommet theme={theme}>
      <Dashboard />
    </Grommet>
  );
}

export default App;
