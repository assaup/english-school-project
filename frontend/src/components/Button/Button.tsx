import type { ReactNode } from 'react'
import styles from './Button.module.scss'

type Button = {
    className?: string
    type: "button" | "submit" | "reset"
    children: ReactNode
    onClick?: () => void
    isDisabled?: boolean
}

const Button = (props: Button) => {
    const {
        className = '',
        type = 'button',
        children,
        onClick,
        isDisabled
    } = props
    return (
        <button
            className={`${className} ${styles.button}`}
            type={type}
            onClick={onClick}
            disabled={isDisabled}
        >
            {children}
        </button>
    )
}

export default Button
