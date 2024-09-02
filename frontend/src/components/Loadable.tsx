import LinearProgress from '@mui/material/LinearProgress';
import { styled } from '@mui/material/styles';
import type { ComponentType, LazyExoticComponent } from 'react';
import { createElement, Suspense } from 'react';

const LoaderWrapper = styled('div')({
  zIndex: 1301,
  width: '100%',
});
const PageLoaderWrapper = styled(LoaderWrapper)({
  position: 'fixed',
  top: 0,
  left: 0,
});

function Loader({ isFullPage = true }: { isFullPage?: boolean }) {
  return isFullPage ? (
    <PageLoaderWrapper>
      <LinearProgress color="primary" />
    </PageLoaderWrapper>
  ) : (
    <LoaderWrapper>
      <LinearProgress color="primary" />
    </LoaderWrapper>
  );
}

type AnyComponent<TProps> =
  | ComponentType<TProps>
  | LazyExoticComponent<ComponentType<TProps>>;

export default function Loadable<TProps>(
  Component: AnyComponent<TProps>,
  isFullPage = true
) {
  return function Loaded(props: TProps) {
    return (
      <Suspense fallback={<Loader isFullPage={isFullPage} />}>
        {createElement(Component as any, props as any)}
      </Suspense>
    );
  };
}
