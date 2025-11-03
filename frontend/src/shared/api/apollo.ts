/**
 * Apollo Client Configuration
 * 
 * This module sets up the Apollo Client for GraphQL communication with the backend.
 * 
 * Configuration:
 * - Endpoint: Configured via VITE_API_URL environment variable or defaults to '/graphql'
 * - Credentials: 'include' ensures JWT cookies are sent with every request
 * - Cache: InMemoryCache for efficient query caching
 * 
 * Usage in Vue components:
 * ```typescript
 * import { useQuery, useMutation } from '@vue/apollo-composable';
 * import { gql } from '@apollo/client/core';
 * 
 * // Query example
 * const { result, loading, error } = useQuery(gql`
 *   query GetCourses {
 *     userCoursesConnection {
 *       id
 *       course {
 *         id
 *         title
 *       }
 *     }
 *   }
 * `);
 * 
 * // Mutation example
 * const { mutate, loading: mutating } = useMutation(gql`
 *   mutation CreateCourse($title: String!) {
 *     courseCreate(title: $title) {
 *       course {
 *         id
 *         title
 *       }
 *     }
 *   }
 * `);
 * ```
 * 
 * @see {@link https://www.apollographql.com/docs/react/} Apollo Client Documentation
 * @see {@link https://v4.apollo.vuejs.org/} Vue Apollo Documentation
 */

import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client/core';

// Create HTTP link for GraphQL endpoint
const httpLink = createHttpLink({
  uri: import.meta.env.VITE_API_URL ?? '/graphql',
  credentials: 'include' // Include cookies for JWT authentication
});

// Initialize Apollo Client
const apolloClient = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache({
    // Type policies for better caching
    typePolicies: {
      Query: {
        fields: {
          // Cache policies for specific queries
          userCoursesConnection: {
            merge(existing = [], incoming) {
              return incoming;
            }
          }
        }
      }
    }
  })
});

export default apolloClient;

