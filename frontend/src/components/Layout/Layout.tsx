import type { ReactNode } from 'react'
import Navbar from '../Navbar/Navbar'
import Footer from '../Footer/Footer'
import styles from './Layout.module.scss'

interface Props {
    children: ReactNode
}

const Layout = ({ children }: Props) => {
    return (
        <div className={styles.wrapper}>
            <Navbar />
            <main className={styles.content}>
                {children}
            </main>
            <Footer />
        </div>
    )
}

export default Layout