import { useQuery } from '@tanstack/react-query'

import {
  getScopeCandidates,
  listAdminApiKeys,
  listMyApiKeys,
} from '../api/apiKeyApi'
import type { GetAdminApiKeysQuery } from '../types'

export function useMyApiKeys() {
  return useQuery({
    queryKey: ['me', 'api-keys'],
    queryFn: listMyApiKeys,
  })
}

export function useScopeCandidates() {
  return useQuery({
    queryKey: ['me', 'api-key-scope-candidates'],
    queryFn: getScopeCandidates,
    staleTime: 5 * 60_000,
  })
}

export function useAdminApiKeys(query: GetAdminApiKeysQuery) {
  return useQuery({
    queryKey: ['admin', 'api-keys', query],
    queryFn: () => listAdminApiKeys(query),
  })
}
