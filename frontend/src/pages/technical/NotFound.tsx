import './NotFound.scss';

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import { FormattedMessage } from 'react-intl';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <Box position="relative">
      <Container className="not-found__container">
        <Typography variant="h1" color="primary" className="not-found__title">
          <FormattedMessage id="not-found-title" />
        </Typography>
        <Typography variant="h5" color="secondary" className="not-found__subtitle">
          <FormattedMessage id="not-found-subtitle" />
        </Typography>
        <Button
          variant="contained"
          color="primary"
          component={Link}
          to="/"
          className="not-found__button"
        >
          <FormattedMessage id="go-home" />
        </Button>
      </Container>
      <div className="not-found__shape1"></div>
      <div className="not-found__shape2"></div>
    </Box>
  );
};

export default NotFound;
