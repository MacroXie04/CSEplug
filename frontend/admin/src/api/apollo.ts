import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

const httpLink = createHttpLink({
  uri: import.meta.env.VITE_API_URL ?? '/graphql',
  credentials: 'include'
});

const apolloClient = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache()
});

export default apolloClient;

